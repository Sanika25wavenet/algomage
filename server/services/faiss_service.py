import faiss
import numpy as np
import logging
import os
from typing import List, Tuple, Optional

logger = logging.getLogger(__name__)

class FaissService:
    """
    Service for managing FAISS vector index operations.
    Encapsulates initialization, adding vectors, searching, and persistence.
    """
    
    def __init__(self, dimension: int = 512, index_path: str = "faiss_index.bin"):
        """
        Initialize the FAISS service.
        
        Args:
            dimension (int): Dimensionality of the embeddings (default 512 for FaceNet).
            index_path (str): File path to save/load the index.
        """
        self.dimension = dimension
        self.index_path = index_path
        self.index = None
        
        if os.path.exists(index_path):
            self.load_index(index_path)
        else:
            # Using IndexFlatL2 for exact search (best for <100k vectors)
            # Requires embeddings to be L2 normalized for cosine capability
            self.index = faiss.IndexFlatL2(dimension)
            logger.info(f"Initialized new FAISS IndexFlatL2 with dimension {dimension}")

    def add_vectors(self, embeddings: List[List[float]]) -> np.ndarray:
        """
        Adds vectors to the FAISS index.
        
        Args:
            embeddings: List of embedding vectors (list of floats).
            
        Returns:
            np.ndarray: Array of IDs (indices) for the added vectors.
            
        Raises:
            ValueError: If embedding dimension does not match index.
        """
        if not embeddings:
            return np.array([])
            
        # Convert to float32 numpy array (FAISS requirement)
        vectors = np.array(embeddings).astype('float32')
        
        # Verify dimension
        if vectors.shape[1] != self.dimension:
            raise ValueError(f"Embedding dimension mismatch. Expected {self.dimension}, got {vectors.shape[1]}")
            
        start_id = self.index.ntotal
        self.index.add(vectors)
        end_id = self.index.ntotal
        
        logger.info(f"Added {len(embeddings)} vectors to FAISS index. Total: {end_id}")
        
        # Return the sequential IDs assigned by IndexFlatL2
        return np.arange(start_id, end_id)

    def search(self, query_vector: List[float], k: int = 5) -> Tuple[List[float], List[int]]:
        """
        Searches for the k nearest neighbors for a single query vector.
        
        Args:
            query_vector: The query embedding.
            k: Number of results to return.
            
        Returns:
            distances (List[float]): L2 distances to the nearest neighbors.
            indices (List[int]): IDs of the nearest neighbors.
        """
        # Convert to 2D float32 array [1, dimension]
        vector = np.array([query_vector]).astype('float32')
        
        if vector.shape[1] != self.dimension:
             raise ValueError(f"Query dimension mismatch. Expected {self.dimension}, got {vector.shape[1]}")
             
        distances, indices = self.index.search(vector, k)
        
        # Return flat lists for easier consumption
        return distances[0].tolist(), indices[0].tolist()

    def save_index(self, file_path: Optional[str] = None):
        """Saves the current index to disk."""
        target_path = file_path or self.index_path
        try:
            faiss.write_index(self.index, target_path)
            logger.info(f"Saved FAISS index to {target_path}")
        except Exception as e:
            logger.error(f"Failed to save FAISS index: {e}")
            raise e

    def load_index(self, file_path: str):
        """Loads an index from disk."""
        try:
            self.index = faiss.read_index(file_path)
            self.dimension = self.index.d
            logger.info(f"Loaded FAISS index from {file_path}. Total vectors: {self.index.ntotal}")
        except Exception as e:
            logger.error(f"Failed to load index from {file_path}: {e}")
            # Fallback to new index to prevent service failure
            logger.warning("Initializing empty index due to load failure.")
            self.index = faiss.IndexFlatL2(self.dimension)

    def reload_index(self):
        """Reloads the index from disk if the file exists."""
        if os.path.exists(self.index_path):
            self.load_index(self.index_path)
        else:
            logger.warning("Index file not found during reload. Keeping current in-memory index.")

# Singleton instance
faiss_service = FaissService()
