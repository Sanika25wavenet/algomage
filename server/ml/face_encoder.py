import torch
from facenet_pytorch import InceptionResnetV1
import numpy as np
from typing import List, Optional, Union
import logging

logger = logging.getLogger(__name__)

class FaceEncoder:
    def __init__(self):
        """
        Initialize FaceNet (InceptionResnetV1) model.
        Pretrained on VGGFace2.
        """
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        logger.info(f"Initializing FaceEncoder on device: {self.device}")
        
        try:
            self.model = InceptionResnetV1(pretrained='vggface2').eval().to(self.device)
        except Exception as e:
            logger.error(f"Failed to initialize FaceNet model: {e}")
            raise

    def encode_faces(self, faces: List[dict]) -> List[dict]:
        """
        Generate embeddings for a list of face detection results.
        
        Args:
            faces: List of dictionaries, each containing:
                   - 'face': torch.Tensor (3x160x160)
                   - 'box': list/np.array
                   - 'confidence': float
                   - (Optional) 'event_id', 'image_id' passed through
        
        Returns:
            List of dictionaries with 'embedding' key added (np.ndarray 512-dim).
            Faces that fail encoding (e.g. NaN) are returned with 'embedding': None.
        """
        if not faces:
            return []

        # Filter faces that have a valid tensor
        valid_indices = []
        tensors = []
        
        for idx, face_data in enumerate(faces):
            tensor = face_data.get('face')
            if tensor is not None and isinstance(tensor, torch.Tensor):
                valid_indices.append(idx)
                tensors.append(tensor)
        
        if not tensors:
            logger.warning("No valid face tensors found in input list.")
            return faces

        try:
            # Batch processing
            embeddings_list = []
            batch_size = 32
            
            for i in range(0, len(tensors), batch_size):
                batch_tensors = tensors[i : i + batch_size]
                batch = torch.stack(batch_tensors).to(self.device)
                
                with torch.no_grad():
                    # Generate embeddings
                    emb_batch = self.model(batch) # (B, 512)
                    
                    # L2 Normalization
                    emb_batch = torch.nn.functional.normalize(emb_batch, p=2, dim=1)
                    
                    # Move to CPU
                    embeddings_list.append(emb_batch.detach().cpu().numpy())
            
            if embeddings_list:
                embeddings_np = np.concatenate(embeddings_list, axis=0).astype(np.float32)
            else:
                embeddings_np = np.array([], dtype=np.float32)
            
            # Validation and Assignment
            for i, real_idx in enumerate(valid_indices):
                if i < len(embeddings_np):
                    emb = embeddings_np[i]
                    
                    # Check for NaNs or Infs
                    if np.any(np.isnan(emb)) or np.any(np.isinf(emb)):
                        logger.error(f"Generated embedding contains NaN/Inf for face index {real_idx}")
                        faces[real_idx]['embedding'] = None
                    else:
                        faces[real_idx]['embedding'] = emb # Already float32
                else:
                    faces[real_idx]['embedding'] = None

        except Exception as e:
            logger.error(f"Error during batch encoding: {e}")
            # Ensure we don't crash, but mark as failed
            for idx in valid_indices:
                faces[idx]['embedding'] = None

        except Exception as e:
            logger.error(f"Error during batch encoding: {e}")
            # Ensure we don't crash, but mark as failed
            for idx in valid_indices:
                faces[idx]['embedding'] = None
                
        return faces

# Singleton instance
face_encoder = FaceEncoder()
