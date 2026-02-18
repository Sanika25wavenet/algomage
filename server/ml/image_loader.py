from PIL import Image, ImageOps, UnidentifiedImageError
import numpy as np
import io
import logging
import os
from typing import List, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ImageLoader:
    def __init__(self, max_dimension: int = 1600, min_dimension: int = 100, max_file_size_mb: int = 15):
        """
        Initialize the ImageLoader.
        Args:
            max_dimension: Maximum width/height for resizing (default 1600px).
            min_dimension: Minimum width/height to process (default 100px).
            max_file_size_mb: Maximum file size allowed in MB (default 15MB).
        """
        self.max_dimension = max_dimension
        self.min_dimension = min_dimension
        self.max_file_size_bytes = max_file_size_mb * 1024 * 1024
        self.allowed_extensions = {".jpg", ".jpeg", ".png", ".webp", ".avif" }

    def _validate_image_size(self, width: int, height: int) -> bool:
        """Check if image dimensions meet the minimum requirement."""
        if width < self.min_dimension or height < self.min_dimension:
            logger.warning(f"Image skipped: Too small ({width}x{height} < {self.min_dimension}px)")
            return False
        return True

    def _validate_file_size_and_ext(self, path: str) -> bool:
        """Check file size and valid extension."""
        # 1. Extension
        ext = os.path.splitext(path)[1].lower()
        if ext not in self.allowed_extensions:
            logger.warning(f"File skipped: Invalid extension '{ext}' for {path}")
            return False
            
        # 2. File Size
        try:
            size_bytes = os.path.getsize(path)
            if size_bytes > self.max_file_size_bytes:
                logger.warning(f"File skipped: Too large ({size_bytes / 1024 / 1024:.2f}MB > {self.max_file_size_bytes / 1024 / 1024}MB)")
                return False
        except OSError:
            logger.warning(f"Could not access file size for {path}")
            return False
            
        return True

    def _process_image(self, image: Image.Image) -> np.ndarray:
        """
        Internal method to standardize image:
        1. Correct Orientation (EXIF).
        2. Convert mode to RGB.
        3. Resize if too large.
        4. Return as numpy array.
        """
        try:
            # 1. Correct Orientation
            image = ImageOps.exif_transpose(image)
        except Exception as e:
            logger.warning(f"Could not correct EXIF orientation: {e}")
            # Proceed with original image if EXIF fails

        # 2. Check Dimensions after loading
        width, height = image.size
        # We check min dimension here too (in case file size was OK but image is tiny)
        if not self._validate_image_size(width, height):
           raise ValueError(f"Image dimensions too small: {width}x{height}")

        # 3. Convert to RGB (removes Alpha channel/Grayscale)
        if image.mode != 'RGB':
            # logger.info(f"Converting image mode {image.mode} to RGB")
            image = image.convert('RGB')

        # 4. Resize if too large for performance optimization
        if max(width, height) > self.max_dimension:
            scale = self.max_dimension / max(width, height)
            new_width = int(width * scale)
            new_height = int(height * scale)
            # logger.info(f"Resizing image from {width}x{height} to {new_width}x{new_height}")
            image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)

        return np.array(image)

    def load_from_path(self, path: str) -> Optional[np.ndarray]:
        """
        Load image from a file path with validations.
        """
        if not self._validate_file_size_and_ext(path):
            return None

        try:
            with Image.open(path) as img:
                img.verify() # Verify file integrity (lightweight)
                
            # Re-open for processing (verify closes file)
            with Image.open(path) as img:
                # Basic load to trigger any corruption errors
                img.load() 
                return self._process_image(img)
                
        except (FileNotFoundError, UnidentifiedImageError, OSError) as e:
            logger.error(f"Failed to load/verify image at {path}: {e}")
            return None
        except ValueError as e:
            # Caught from _process_image validation
            # logger.warning(str(e))
            return None
        except Exception as e:
            logger.error(f"Unexpected error loading image from path {path}: {e}")
            return None

    def load_from_bytes(self, data: bytes) -> Optional[np.ndarray]:
        """
        Load image from bytes (standard for API uploads).
        """
        if not data:
            logger.error("Received empty bytes data for image loading.")
            return None
        
        if len(data) > self.max_file_size_bytes:
             logger.warning(f"Bytes load skipped: Too large ({len(data)} bytes)")
             return None

        try:
            with Image.open(io.BytesIO(data)) as img:
                img.load()
                return self._process_image(img)
        except UnidentifiedImageError:
            logger.error("Data provided is not a valid image format.")
            return None
        except ValueError as e:
            # logger.warning(str(e))
            return None
        except Exception as e:
            logger.error(f"Error loading image from bytes: {e}")
            return None
            
    def load_batch(self, paths: List[str]) -> List[np.ndarray]:
        """
        Load a batch of images from paths.
        Skips invalid/corrupt images silently (logged).
        Returns list of valid numpy arrays.
        """
        images = []
        for path in paths:
            img = self.load_from_path(path)
            if img is not None:
                images.append(img)
        logger.info(f"Batch loaded {len(images)} valid images from {len(paths)} paths.")
        return images

# Singleton instance
image_loader = ImageLoader()
