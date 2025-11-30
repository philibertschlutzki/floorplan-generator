"""Image preprocessing module for building analysis.

This module handles:
- Image loading and validation
- Perspective correction
- Noise reduction and enhancement
- Edge detection preparation
- Scale detection from reference objects

Example:
    >>> from cv_modules import ImagePreprocessor
    >>> preprocessor = ImagePreprocessor()
    >>> processed_img = preprocessor.process("building.jpg")
    >>> scale = preprocessor.detect_scale(processed_img)
"""

import cv2
import numpy as np
from typing import Tuple, Optional, Dict, Any
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class ImagePreprocessor:
    """Preprocesses building images for feature detection.
    
    This class provides methods to prepare images for architectural
    feature extraction by applying various image processing techniques.
    
    Attributes:
        target_size (Tuple[int, int]): Target image size for processing
        gaussian_kernel (int): Kernel size for Gaussian blur
        clahe_clip_limit (float): CLAHE contrast enhancement limit
    """
    
    def __init__(
        self,
        target_size: Tuple[int, int] = (1920, 1080),
        gaussian_kernel: int = 5,
        clahe_clip_limit: float = 2.0
    ):
        """Initialize the ImagePreprocessor.
        
        Args:
            target_size: Target dimensions for resizing images
            gaussian_kernel: Kernel size for Gaussian blur (must be odd)
            clahe_clip_limit: Contrast limit for CLAHE algorithm
        
        Raises:
            ValueError: If gaussian_kernel is not odd
        """
        if gaussian_kernel % 2 == 0:
            raise ValueError("Gaussian kernel size must be odd")
        
        self.target_size = target_size
        self.gaussian_kernel = gaussian_kernel
        self.clahe_clip_limit = clahe_clip_limit
        self.clahe = cv2.createCLAHE(
            clipLimit=clahe_clip_limit,
            tileGridSize=(8, 8)
        )
        logger.info(f"ImagePreprocessor initialized with target_size={target_size}")
    
    def load_image(self, image_path: str) -> Optional[np.ndarray]:
        """Load an image from file path.
        
        Args:
            image_path: Path to the image file
        
        Returns:
            Loaded image as numpy array, or None if loading failed
        
        Raises:
            FileNotFoundError: If image file doesn't exist
        """
        path = Path(image_path)
        if not path.exists():
            raise FileNotFoundError(f"Image not found: {image_path}")
        
        img = cv2.imread(str(path))
        if img is None:
            logger.error(f"Failed to load image: {image_path}")
            return None
        
        logger.info(f"Loaded image: {image_path}, shape={img.shape}")
        return img
    
    def resize_image(
        self,
        image: np.ndarray,
        maintain_aspect: bool = True
    ) -> np.ndarray:
        """Resize image to target size.
        
        Args:
            image: Input image
            maintain_aspect: Whether to maintain aspect ratio
        
        Returns:
            Resized image
        """
        if maintain_aspect:
            h, w = image.shape[:2]
            target_w, target_h = self.target_size
            
            # Calculate scaling factor
            scale = min(target_w / w, target_h / h)
            new_w, new_h = int(w * scale), int(h * scale)
            
            resized = cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_AREA)
            logger.debug(f"Resized with aspect ratio: {image.shape} -> {resized.shape}")
        else:
            resized = cv2.resize(image, self.target_size, interpolation=cv2.INTER_AREA)
            logger.debug(f"Resized to fixed size: {image.shape} -> {resized.shape}")
        
        return resized
    
    def correct_perspective(
        self,
        image: np.ndarray,
        auto_detect: bool = True
    ) -> Tuple[np.ndarray, Optional[np.ndarray]]:
        """Apply perspective correction to image.
        
        Args:
            image: Input image
            auto_detect: If True, automatically detect corners
        
        Returns:
            Tuple of (corrected_image, transformation_matrix)
        """
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        if auto_detect:
            # Detect edges
            edges = cv2.Canny(gray, 50, 150, apertureSize=3)
            
            # Find contours
            contours, _ = cv2.findContours(
                edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
            )
            
            if not contours:
                logger.warning("No contours found for perspective correction")
                return image, None
            
            # Find largest quadrilateral
            max_area = 0
            best_contour = None
            
            for contour in contours:
                area = cv2.contourArea(contour)
                if area > max_area:
                    peri = cv2.arcLength(contour, True)
                    approx = cv2.approxPolyDP(contour, 0.02 * peri, True)
                    if len(approx) == 4:
                        max_area = area
                        best_contour = approx
            
            if best_contour is None:
                logger.warning("No quadrilateral found for perspective correction")
                return image, None
            
            # Order points: top-left, top-right, bottom-right, bottom-left
            pts = best_contour.reshape(4, 2)
            rect = self._order_points(pts)
            
            # Compute destination points
            (tl, tr, br, bl) = rect
            widthA = np.linalg.norm(br - bl)
            widthB = np.linalg.norm(tr - tl)
            maxWidth = max(int(widthA), int(widthB))
            
            heightA = np.linalg.norm(tr - br)
            heightB = np.linalg.norm(tl - bl)
            maxHeight = max(int(heightA), int(heightB))
            
            dst = np.array([
                [0, 0],
                [maxWidth - 1, 0],
                [maxWidth - 1, maxHeight - 1],
                [0, maxHeight - 1]
            ], dtype="float32")
            
            # Compute perspective transform
            M = cv2.getPerspectiveTransform(rect, dst)
            warped = cv2.warpPerspective(image, M, (maxWidth, maxHeight))
            
            logger.info(f"Perspective correction applied: {image.shape} -> {warped.shape}")
            return warped, M
        
        return image, None
    
    def _order_points(self, pts: np.ndarray) -> np.ndarray:
        """Order points in clockwise order starting from top-left.
        
        Args:
            pts: Array of 4 points
        
        Returns:
            Ordered points [top-left, top-right, bottom-right, bottom-left]
        """
        rect = np.zeros((4, 2), dtype="float32")
        
        # Top-left has smallest sum, bottom-right has largest sum
        s = pts.sum(axis=1)
        rect[0] = pts[np.argmin(s)]
        rect[2] = pts[np.argmax(s)]
        
        # Top-right has smallest difference, bottom-left has largest
        diff = np.diff(pts, axis=1)
        rect[1] = pts[np.argmin(diff)]
        rect[3] = pts[np.argmax(diff)]
        
        return rect
    
    def enhance_image(self, image: np.ndarray) -> np.ndarray:
        """Apply enhancement techniques to improve feature detection.
        
        Args:
            image: Input image
        
        Returns:
            Enhanced image
        """
        # Convert to LAB color space
        lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        
        # Apply CLAHE to L channel
        l_clahe = self.clahe.apply(l)
        
        # Merge channels
        enhanced_lab = cv2.merge([l_clahe, a, b])
        enhanced = cv2.cvtColor(enhanced_lab, cv2.COLOR_LAB2BGR)
        
        logger.debug("Applied CLAHE enhancement")
        return enhanced
    
    def denoise_image(self, image: np.ndarray) -> np.ndarray:
        """Apply denoising to reduce image noise.
        
        Args:
            image: Input image
        
        Returns:
            Denoised image
        """
        denoised = cv2.fastNlMeansDenoisingColored(
            image, None, 10, 10, 7, 21
        )
        logger.debug("Applied denoising")
        return denoised
    
    def detect_scale(
        self,
        image: np.ndarray,
        reference_length_meters: Optional[float] = None
    ) -> Dict[str, Any]:
        """Detect scale from reference objects or markers in image.
        
        Args:
            image: Input image
            reference_length_meters: Known length of reference object in meters
        
        Returns:
            Dictionary containing scale information:
                - pixels_per_meter: Conversion factor
                - confidence: Detection confidence (0-1)
                - method: Detection method used
        """
        # TODO: Implement advanced scale detection
        # For now, return default scale assumption
        return {
            "pixels_per_meter": 100.0,  # Default assumption
            "confidence": 0.5,
            "method": "default"
        }
    
    def process(
        self,
        image_path: str,
        apply_perspective: bool = True,
        apply_enhancement: bool = True,
        apply_denoising: bool = True
    ) -> Tuple[np.ndarray, Dict[str, Any]]:
        """Complete preprocessing pipeline.
        
        Args:
            image_path: Path to input image
            apply_perspective: Whether to apply perspective correction
            apply_enhancement: Whether to apply image enhancement
            apply_denoising: Whether to apply denoising
        
        Returns:
            Tuple of (processed_image, metadata_dict)
        
        Raises:
            FileNotFoundError: If image file doesn't exist
        """
        logger.info(f"Starting preprocessing pipeline for: {image_path}")
        
        # Load image
        img = self.load_image(image_path)
        if img is None:
            raise ValueError(f"Failed to load image: {image_path}")
        
        metadata = {
            "original_shape": img.shape,
            "steps_applied": []
        }
        
        # Resize
        img = self.resize_image(img)
        metadata["steps_applied"].append("resize")
        
        # Perspective correction
        if apply_perspective:
            img, transform_matrix = self.correct_perspective(img)
            metadata["perspective_corrected"] = transform_matrix is not None
            metadata["steps_applied"].append("perspective")
        
        # Enhancement
        if apply_enhancement:
            img = self.enhance_image(img)
            metadata["steps_applied"].append("enhancement")
        
        # Denoising
        if apply_denoising:
            img = self.denoise_image(img)
            metadata["steps_applied"].append("denoising")
        
        # Detect scale
        scale_info = self.detect_scale(img)
        metadata["scale"] = scale_info
        
        metadata["final_shape"] = img.shape
        logger.info(f"Preprocessing complete. Applied: {metadata['steps_applied']}")
        
        return img, metadata
