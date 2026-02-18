import torch
from facenet_pytorch import MTCNN
import numpy as np
from typing import List, Dict, Optional, Union
import logging
from PIL import Image, ImageDraw, ImageFont

logger = logging.getLogger(__name__)

class FaceDetector:
    def __init__(self, min_face_size: int = 20, thresholds: List[float] = [0.6, 0.7, 0.7]):
        """
        Initialize MTCNN Face Detector.
        Args:
            min_face_size: Minimum face size in pixels to detect.
            thresholds: MTCNN thresholds for P-Net, R-Net, O-Net.
        """
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        logger.info(f"Initializing FaceDetector on device: {self.device}")
        
        try:
            self.mtcnn = MTCNN(
                keep_all=True,          # Detect multiple faces
                min_face_size=min_face_size,
                thresholds=thresholds,
                post_process=True,      # Normalizes face tensors
                device=self.device
            )
        except Exception as e:
            logger.error(f"Failed to initialize MTCNN: {e}")
            raise

    def _validate_box(self, box: List[float], image_shape: tuple) -> List[int]:
        """
        Clamp bounding box coordinates to be within image dimensions.
        """
        h, w = image_shape[:2]
        x1, y1, x2, y2 = box
        
        # Clamp coordinates
        x1 = max(0, int(x1))
        y1 = max(0, int(y1))
        x2 = min(w, int(x2))
        y2 = min(h, int(y2))
        
        return [x1, y1, x2, y2]

    def detect_faces(self, image: np.ndarray, min_confidence: float = 0.90) -> List[Dict]:
        """
        Detect faces in a numpy array image (RGB).
        Args:
            image: Standard numpy array (H, W, 3).
            min_confidence: Minimum confidence threshold to accept a detection.
        Returns:
            List of dicts: {'box': [x1, y1, x2, y2], 'confidence': float, 'face': tensor}
        """
        if image is None:
            logger.warning("FaceDetector received None image.")
            return []

        try:
            # 1. Detect boxes and probabilities
            boxes, probs = self.mtcnn.detect(image)
            
            results = []
            if boxes is not None and len(boxes) > 0:
                # 2. Get face tensors ONLY for valid boxes (This is faster)
                # Using mtcnn.extract for efficiency
                from PIL import Image
                pil_img = Image.fromarray(image)
                
                for i, box in enumerate(boxes):
                    prob = probs[i]
                    if prob is None or prob < min_confidence: 
                        continue
                    
                    # Validate box
                    valid_box = self._validate_box(box, image.shape)
                    
                    # Size Filtering
                    box_w = valid_box[2] - valid_box[0]
                    box_h = valid_box[3] - valid_box[1]
                    if box_w < 20 or box_h < 20:
                        continue

                    # Extract face tensor manually or using mtcnn.extract
                    # mtcnn.extract returns cropped face normalized/resized to 160x160
                    face_tensor = self.mtcnn.extract(pil_img, [valid_box], save_path=None)
                    if face_tensor is not None:
                        # face_tensor is (1, 3, 160, 160)
                        face_tensor = face_tensor[0]
                    
                    results.append({
                        'box': valid_box,
                        'confidence': float(prob),
                        'face': face_tensor
                    })
                    
                logger.info(f"Detected {len(results)} valid faces.")
            else:
                logger.info("No faces detected.")

            return results

        except Exception as e:
            logger.error(f"Error during face detection: {e}")
            return []

    def draw_boxes(self, image: np.ndarray, results: List[Dict]) -> Image.Image:
        """
        Draw bounding boxes on the image for visualization.
        """
        if isinstance(image, np.ndarray):
            pil_img = Image.fromarray(image)
        else:
            pil_img = image

        draw = ImageDraw.Draw(pil_img)
        
        for res in results:
            box = res['box']
            conf = res['confidence']
            
            # Draw Box
            draw.rectangle(box, outline="red", width=3)
            
            # Draw Text
            text = f"{conf:.2f}"
            # Simple text positioning
            draw.text((box[0], box[1] - 10), text, fill="red")
            
        return pil_img

    def process_batch(self, images: List[np.ndarray]) -> List[List[Dict]]:
        """
        Process a batch of images sequentially.
        (MTCNN batch inference is complex with variable image sizes, so currently sequential).
        """
        batch_results = []
        for img in images:
            batch_results.append(self.detect_faces(img))
        return batch_results

# Singleton instance
face_detector = FaceDetector()
