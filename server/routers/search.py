from fastapi import APIRouter, UploadFile, File, HTTPException, status
from ml.image_loader import image_loader
from ml.face_detector import face_detector
from ml.face_encoder import face_encoder
from ml.quality_checker import quality_checker
from services.faiss_service import faiss_service
from config.database import db
from config.settings import settings
import numpy as np
import torch
import logging
from PIL import Image
import io
import os

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/search", tags=["Search"])

def preprocess_image(image_array: np.ndarray) -> np.ndarray:
    """
    Placeholder for preprocessing function.
    To be implemented later.
    """
    # Currently just returns the image as is
    return image_array

def load_image_from_bytes(file_bytes: bytes) -> np.ndarray:
    """
    Step 2: Convert image bytes to NumPy array.
    1. Uses PIL to open image from bytes
    2. Converts image to RGB format
    3. Converts image to NumPy array
    4. Returns NumPy image array
    """
    image = Image.open(io.BytesIO(file_bytes))
    image = image.convert("RGB")
    return np.array(image)

def detect_face(image_array: np.ndarray) -> dict:
    """
    Step 3: Detect face using MTCNN.
    1. Uses MTCNN to detect faces
    2. Returns: bounding box, confidence score
    3. If no face found -> raise HTTPException
    4. If multiple faces -> select highest confidence face
    """
    detections = face_detector.detect_faces(image_array)
    
    if not detections:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No face detected in the selfie. Please ensure your face is clearly visible."
        )
    
    # If multiple faces, select the one with the highest confidence
    if len(detections) > 1:
        logger.info(f"Multiple faces ({len(detections)}) detected. Selecting highest confidence.")
        best_face = max(detections, key=lambda x: x['confidence'])
        return best_face
    
    return detections[0]

def crop_face(image_array: np.ndarray, bounding_box: list) -> np.ndarray:
    """
    Step 4: Crop face using bounding box.
    1. Takes full image and bounding box [x1, y1, x2, y2]
    2. Crops face region from image
    3. Handles boundary overflow safely
    4. Returns cropped face image
    """
    h, w = image_array.shape[:2]
    x1, y1, x2, y2 = bounding_box
    
    # Clip coordinates to image boundaries
    x1 = max(0, int(x1))
    y1 = max(0, int(y1))
    x2 = min(w, int(x2))
    y2 = min(h, int(y2))
    
    return image_array[y1:y2, x1:x2]

def get_public_url(file_path: str) -> str:
    """
    Convert an absolute file path to a public URL.
    Assumes files are under the 'uploads' directory.
    """
    # Normalize path to use forward slashes for URLs
    file_path = file_path.replace("\\", "/")
    
    # Extract the part starting from 'uploads'
    if "uploads/" in file_path:
        relative_path = file_path.split("uploads/")[1]
        return f"{settings.BASE_URL}/uploads/{relative_path}"
    
    return file_path

@router.post("/")
async def search_by_selfie(
    event_id: str,
    selfie: UploadFile = File(...)
):
    """
    Upload a selfie to search for matching photos in a specific event.
    - event_id: ID of the event to search within.
    - selfie: The user's selfie image.
    """
    # 1. Validate file exists and is an image
    if not selfie:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No selfie file provided"
        )
    
    if not selfie.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type: {selfie.content_type}. Please upload an image."
        )

    try:
        # 2. Read file bytes
        contents = await selfie.read()
        
        # 3. Step 2: Convert bytes to NumPy array
        image_array = load_image_from_bytes(contents)
        
        if image_array is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to process image. It might be corrupt or an unsupported format."
            )

        # 4. Step 3: Face Detection
        face_data = detect_face(image_array)
        
        # 5. Step 4: Crop Face
        face_crop = crop_face(image_array, face_data['box'])
        
        # 6. Quality Check
        quality_result = quality_checker.check_face(face_crop)
        
        if not quality_result['is_valid']:
            issues_str = ", ".join(quality_result['issues'])
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Selfie quality too low: {issues_str}. Please take a clearer photo."
            )

        # 6. Face Encoding (Generate 512-dim embedding)
        # encode_faces expects a list of detection results
        encoded_faces = face_encoder.encode_faces([face_data])
        embedding = encoded_faces[0].get('embedding')
        
        if embedding is None:
             raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to generate face embedding."
            )

        # 7. Perform Search in FAISS
        # Reload index to get latest data
        faiss_service.reload_index()
        
        # Search for top matches (get more than needed to filter by event_id)
        # 1.0 is a reasonable squared L2 distance threshold for FaceNet
        MAX_DISTANCE = 0.8 
        K_SEARCH = 100
        
        distances, indices = faiss_service.search(embedding.tolist(), k=K_SEARCH)
        
        # Filter by distance threshold
        valid_results = [
            (idx, dist) for idx, dist in zip(indices, distances) 
            if idx != -1 and dist <= MAX_DISTANCE
        ]
        
        if not valid_results:
            return {
                "status": "success",
                "message": "No matches found in the system.",
                "results": []
            }

        # 8. Query MongoDB to filter by event_id and get metadata
        matched_faiss_ids = [r[0] for r in valid_results]
        id_to_distance = {r[0]: r[1] for r in valid_results}
        
        # Find records matching these FAISS IDs correctly scoped to the event_id
        cursor = db.db.faces.find({
            "image_embedded_number": {"$in": matched_faiss_ids},
            "event_id": event_id
        })
        
        face_records = await cursor.to_list(length=K_SEARCH)
        
        # 9. Format Results
        # Group by file_path to avoid duplicates if multiple people were matched in the same photo
        # (Though with a single query selfie, we just want photos containing THIS person)
        unique_photos = {}
        
        for record in face_records:
            path = record['file_path']
            faiss_id = record['image_embedded_number']
            distance = id_to_distance.get(faiss_id, float('inf'))
            
            # If photo already added, keep the one with better distance
            if path not in unique_photos or distance < unique_photos[path]['distance']:
                unique_photos[path] = {
                    "photo_url": get_public_url(path),
                    "distance": float(distance),
                    "confidence": float(record.get('confidence', 0))
                }
        
        # Sort by distance (ascending)
        sorted_results = sorted(unique_photos.values(), key=lambda x: x['distance'])

        return {
            "status": "success",
            "message": f"Found {len(sorted_results)} matching photos",
            "event_id": event_id,
            "results": sorted_results
        }

    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error in search_by_selfie: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )
