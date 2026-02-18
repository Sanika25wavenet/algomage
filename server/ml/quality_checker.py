import cv2
import numpy as np
import logging

logger = logging.getLogger(__name__)

class FaceQualityChecker:
    def __init__(self, blur_threshold: float = 100.0, darkness_threshold: float = 40.0):
        """
        Initialize FaceQualityChecker.
        Args:
            blur_threshold: Variance of Laplacian measure. Below this = blurry.
            darkness_threshold: Average pixel intensity. Below this = too dark.
        """
        self.blur_threshold = blur_threshold
        self.darkness_threshold = darkness_threshold

    def is_blurry(self, image: np.ndarray) -> (bool, float):
        """
        Check if an image is blurry.
        Returns: (is_blurry, variance_score)
        """
        try:
            if image is None or image.size == 0:
                return True, 0.0
            
            # Convert to gray
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
            else:
                gray = image
                
            # Compute Laplacian Variance
            score = cv2.Laplacian(gray, cv2.CV_64F).var()
            return score < self.blur_threshold, score
        except Exception as e:
            logger.error(f"Error checking blur: {e}")
            return True, 0.0

    def is_too_dark(self, image: np.ndarray) -> (bool, float):
        """
        Check if an image is too dark.
        Returns: (is_too_dark, brightness_score)
        """
        try:
            if image is None or image.size == 0:
                return True, 0.0
            
            # Convert to HSV if possible for V channel, else average gray
            # Simple approach: Average pixel intensity
            if len(image.shape) == 3:
                # RGB to HSV
                hsv = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)
                # V channel is brightness
                brightness = hsv[..., 2].mean()
            else:
                brightness = image.mean()
                
            return brightness < self.darkness_threshold, brightness
        except Exception as e:
            logger.error(f"Error checking darkness: {e}")
            return True, 0.0

    def check_face(self, image: np.ndarray) -> dict:
        """
        Validate a detected face crop.
        Returns dictionary with 'is_valid' and 'issues'.
        """
        is_valid = True
        issues = []
        
        # Blur check
        blurry, blur_score = self.is_blurry(image)
        if blurry:
            is_valid = False
            issues.append(f"Too Blurry (Score: {blur_score:.1f} < {self.blur_threshold})")
            
        # Darkness check
        dark, dark_score = self.is_too_dark(image)
        if dark:
            is_valid = False
            issues.append(f"Too Dark (Score: {dark_score:.1f} < {self.darkness_threshold})")
            
        return {
            "is_valid": is_valid,
            "issues": issues,
            "scores": {"blur": blur_score, "brightness": dark_score}
        }

# Singleton
quality_checker = FaceQualityChecker()
