"""Tests for ImagePreprocessor module."""

import unittest
import numpy as np
import cv2
from pathlib import Path
import sys
import tempfile

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from cv_modules.image_preprocessor import ImagePreprocessor


class TestImagePreprocessor(unittest.TestCase):
    """Test cases for ImagePreprocessor class."""
    
    @classmethod
    def setUpClass(cls):
        """Create test images for all tests."""
        cls.test_dir = Path(tempfile.mkdtemp())
        
        # Create a simple test image
        cls.test_image = np.zeros((600, 800, 3), dtype=np.uint8)
        cv2.rectangle(cls.test_image, (100, 100), (700, 500), (255, 255, 255), -1)
        
        cls.test_image_path = cls.test_dir / "test_image.png"
        cv2.imwrite(str(cls.test_image_path), cls.test_image)
    
    def test_initialization(self):
        """Test preprocessor initialization."""
        preprocessor = ImagePreprocessor()
        self.assertIsNotNone(preprocessor)
        self.assertEqual(preprocessor.target_size, (1920, 1080))
    
    def test_invalid_kernel_size(self):
        """Test that even kernel sizes raise ValueError."""
        with self.assertRaises(ValueError):
            ImagePreprocessor(gaussian_kernel=4)
    
    def test_load_image(self):
        """Test image loading."""
        preprocessor = ImagePreprocessor()
        img = preprocessor.load_image(str(self.test_image_path))
        self.assertIsNotNone(img)
        self.assertEqual(img.shape[2], 3)  # BGR image
    
    def test_load_nonexistent_image(self):
        """Test loading nonexistent image raises error."""
        preprocessor = ImagePreprocessor()
        with self.assertRaises(FileNotFoundError):
            preprocessor.load_image("nonexistent.jpg")
    
    def test_resize_image(self):
        """Test image resizing."""
        preprocessor = ImagePreprocessor(target_size=(800, 600))
        resized = preprocessor.resize_image(self.test_image)
        self.assertLessEqual(resized.shape[0], 600)
        self.assertLessEqual(resized.shape[1], 800)
    
    def test_enhance_image(self):
        """Test image enhancement."""
        preprocessor = ImagePreprocessor()
        enhanced = preprocessor.enhance_image(self.test_image)
        self.assertEqual(enhanced.shape, self.test_image.shape)
    
    def test_denoise_image(self):
        """Test image denoising."""
        preprocessor = ImagePreprocessor()
        denoised = preprocessor.denoise_image(self.test_image)
        self.assertEqual(denoised.shape, self.test_image.shape)
    
    def test_detect_scale(self):
        """Test scale detection."""
        preprocessor = ImagePreprocessor()
        scale_info = preprocessor.detect_scale(self.test_image)
        self.assertIn('pixels_per_meter', scale_info)
        self.assertIn('confidence', scale_info)
        self.assertGreater(scale_info['pixels_per_meter'], 0)
    
    def test_complete_pipeline(self):
        """Test complete preprocessing pipeline."""
        preprocessor = ImagePreprocessor()
        processed, metadata = preprocessor.process(
            str(self.test_image_path),
            apply_perspective=False,  # Skip for simple test image
            apply_enhancement=True,
            apply_denoising=True
        )
        
        self.assertIsNotNone(processed)
        self.assertIn('steps_applied', metadata)
        self.assertIn('scale', metadata)
        self.assertTrue(len(metadata['steps_applied']) > 0)


if __name__ == '__main__':
    unittest.main()
