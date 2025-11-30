"""Integration tests for complete pipeline."""

import unittest
import numpy as np
import cv2
import tempfile
import json
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from cv_modules import (
    ImagePreprocessor,
    FeatureDetector,
    DimensionExtractor,
    ConfigGenerator
)


class TestPipelineIntegration(unittest.TestCase):
    """Integration tests for complete image-to-config pipeline."""
    
    @classmethod
    def setUpClass(cls):
        """Create test image and temporary directory."""
        cls.test_dir = Path(tempfile.mkdtemp())
        
        # Create a realistic test image
        cls.test_image = np.ones((800, 1000, 3), dtype=np.uint8) * 255
        
        # Draw building structure
        # Stone foundation (gray)
        cv2.rectangle(cls.test_image, (100, 400), (900, 700), (150, 150, 150), -1)
        cv2.rectangle(cls.test_image, (100, 400), (900, 700), (80, 80, 80), 3)
        
        # Wood section (brown)
        cv2.rectangle(cls.test_image, (100, 200), (900, 400), (139, 90, 43), -1)
        cv2.rectangle(cls.test_image, (100, 200), (900, 400), (80, 50, 20), 3)
        
        # Windows
        for x in [250, 450, 650]:
            cv2.rectangle(cls.test_image, (x, 250), (x+80, 330), (50, 50, 150), -1)
            cv2.rectangle(cls.test_image, (x, 250), (x+80, 330), (20, 20, 80), 2)
        
        # Door
        cv2.rectangle(cls.test_image, (450, 500), (550, 680), (70, 40, 20), -1)
        cv2.rectangle(cls.test_image, (450, 500), (550, 680), (40, 20, 10), 3)
        
        # Roof
        roof_peak = (500, 100)
        cv2.line(cls.test_image, roof_peak, (100, 200), (0, 0, 200), 8)
        cv2.line(cls.test_image, roof_peak, (900, 200), (0, 0, 200), 8)
        
        # Save test image
        cls.test_image_path = cls.test_dir / "test_building.png"
        cv2.imwrite(str(cls.test_image_path), cls.test_image)
    
    def test_complete_pipeline(self):
        """Test complete image-to-config pipeline."""
        # Step 1: Preprocess
        preprocessor = ImagePreprocessor()
        processed_img, metadata = preprocessor.process(
            str(self.test_image_path),
            apply_perspective=False,  # Simple test image doesn't need correction
            apply_enhancement=True,
            apply_denoising=False  # Skip for faster testing
        )
        
        self.assertIsNotNone(processed_img)
        self.assertIn('steps_applied', metadata)
        
        # Step 2: Detect features
        detector = FeatureDetector()
        detections = detector.detect_all(processed_img)
        
        self.assertIn('windows', detections)
        self.assertIn('doors', detections)
        self.assertIn('walls', detections)
        
        # Step 3: Extract dimensions
        extractor = DimensionExtractor(pixels_per_meter=100.0)
        dimensions_result = extractor.extract(
            detections,
            processed_img.shape,
            metadata.get('scale')
        )
        
        self.assertIn('dimensions', dimensions_result)
        self.assertIn('confidence', dimensions_result)
        self.assertGreater(dimensions_result['confidence'], 0)
        
        # Step 4: Generate config
        generator = ConfigGenerator()
        config = generator.generate(
            dimensions_result['dimensions'],
            building_type='Alpine Sennhütte',
            metadata={
                'extraction_confidence': dimensions_result['confidence'],
                'test_run': True
            }
        )
        
        self.assertIn('timestamp', config)
        self.assertIn('building_type', config)
        self.assertIn('dimensions', config)
        
        # Step 5: Save and validate
        output_path = self.test_dir / "integration_test_config.json"
        success = generator.save_config(config, str(output_path))
        
        self.assertTrue(success)
        self.assertTrue(output_path.exists())
        
        # Validate saved config
        loaded_config = generator.load_config(str(output_path))
        is_valid, errors = generator.validate_config(loaded_config)
        
        self.assertTrue(is_valid)
        self.assertEqual(len(errors), 0)
    
    def test_pipeline_with_custom_scale(self):
        """Test pipeline with custom scale parameter."""
        preprocessor = ImagePreprocessor()
        processed_img, _ = preprocessor.process(
            str(self.test_image_path),
            apply_perspective=False
        )
        
        detector = FeatureDetector()
        detections = detector.detect_all(processed_img)
        
        # Use custom scale
        custom_scale = 120.0
        extractor = DimensionExtractor(pixels_per_meter=custom_scale)
        result = extractor.extract(
            detections,
            processed_img.shape,
            {'pixels_per_meter': custom_scale}
        )
        
        self.assertEqual(result['scale_used'], custom_scale)
    
    def test_pipeline_error_handling(self):
        """Test pipeline error handling with invalid input."""
        preprocessor = ImagePreprocessor()
        
        with self.assertRaises(FileNotFoundError):
            preprocessor.process("nonexistent_file.jpg")


if __name__ == '__main__':
    unittest.main()
