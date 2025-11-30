"""Tests for DimensionExtractor module."""

import unittest
import numpy as np
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from cv_modules.dimension_extractor import DimensionExtractor


class TestDimensionExtractor(unittest.TestCase):
    """Test cases for DimensionExtractor class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.extractor = DimensionExtractor(pixels_per_meter=100.0)
        
        # Mock detection results
        self.mock_detections = {
            'windows': [
                {'bbox': {'x': 100, 'y': 100, 'width': 80, 'height': 80}, 'properties': {}},
                {'bbox': {'x': 200, 'y': 100, 'width': 80, 'height': 80}, 'properties': {}},
            ],
            'doors': [
                {'bbox': {'x': 400, 'y': 400, 'width': 150, 'height': 200}, 'properties': {}}
            ],
            'roof': {
                'pitch_angle': 45.0,
                'confidence': 0.8
            },
            'walls': {
                'stone': [{
                    'feature_type': 'stone_wall',
                    'bbox': {'x': 0, 'y': 400, 'width': 800, 'height': 200},
                    'properties': {}
                }],
                'wood': [{
                    'feature_type': 'wood_wall',
                    'bbox': {'x': 0, 'y': 200, 'width': 800, 'height': 200},
                    'properties': {}
                }]
            }
        }
        
        self.image_shape = (600, 800, 3)
    
    def test_initialization(self):
        """Test extractor initialization."""
        self.assertEqual(self.extractor.pixels_per_meter, 100.0)
        self.assertIsNotNone(self.extractor.default_dimensions)
    
    def test_pixels_to_meters(self):
        """Test pixel to meter conversion."""
        result = self.extractor.pixels_to_meters(100)
        self.assertEqual(result, 1.0)
        
        result = self.extractor.pixels_to_meters(250)
        self.assertEqual(result, 2.5)
    
    def test_extract_foundation_dimensions(self):
        """Test foundation dimension extraction."""
        length, width, conf = self.extractor.extract_foundation_dimensions(
            self.image_shape,
            self.mock_detections['walls']
        )
        
        self.assertGreater(length, 0)
        self.assertGreater(width, 0)
        self.assertGreater(conf, 0)
        self.assertLessEqual(conf, 1.0)
    
    def test_extract_wall_heights(self):
        """Test wall height extraction."""
        stone_h, wood_h, conf = self.extractor.extract_wall_heights(
            self.mock_detections['walls'],
            self.image_shape[0]
        )
        
        self.assertGreater(stone_h, 0)
        self.assertGreater(wood_h, 0)
        self.assertGreater(conf, 0)
    
    def test_extract_window_dimensions(self):
        """Test window dimension extraction."""
        width, height, count, conf = self.extractor.extract_window_dimensions(
            self.mock_detections['windows']
        )
        
        self.assertGreater(width, 0)
        self.assertGreater(height, 0)
        self.assertEqual(count, 2)
        self.assertGreater(conf, 0)
    
    def test_extract_door_dimensions(self):
        """Test door dimension extraction."""
        width, height, offset, conf = self.extractor.extract_door_dimensions(
            self.mock_detections['doors'],
            foundation_width=8.0
        )
        
        self.assertGreater(width, 0)
        self.assertGreater(height, 0)
        self.assertGreaterEqual(offset, 0)
        self.assertGreater(conf, 0)
    
    def test_extract_roof_parameters(self):
        """Test roof parameter extraction."""
        angle, overhang, conf = self.extractor.extract_roof_parameters(
            self.mock_detections['roof']
        )
        
        self.assertEqual(angle, 45.0)
        self.assertGreater(overhang, 0)
        self.assertGreater(conf, 0)
    
    def test_validate_dimensions_valid(self):
        """Test validation with valid dimensions."""
        valid_dims = {
            'foundation_length': 8.5,
            'foundation_width': 7.0,
            'stone_section_height': 1.8,
            'wood_section_height': 2.5,
            'door_height': 1.5,
            'wood_window_width': 1.0,
            'wood_window_height': 1.0,
            'roof_pitch_angle': 45.0
        }
        
        is_valid, warnings = self.extractor.validate_dimensions(valid_dims)
        self.assertTrue(is_valid)
    
    def test_validate_dimensions_warnings(self):
        """Test validation with problematic dimensions."""
        invalid_dims = {
            'foundation_length': 25.0,  # Too large
            'foundation_width': 7.0,
            'stone_section_height': 1.8,
            'wood_section_height': 2.5,
            'door_height': 2.0,  # Exceeds stone section
            'wood_window_width': 1.0,
            'wood_window_height': 1.0,
            'roof_pitch_angle': 80.0  # Too steep
        }
        
        is_valid, warnings = self.extractor.validate_dimensions(invalid_dims)
        self.assertTrue(len(warnings) > 0)
    
    def test_complete_extraction(self):
        """Test complete dimension extraction pipeline."""
        result = self.extractor.extract(
            self.mock_detections,
            self.image_shape,
            scale_info={'pixels_per_meter': 100.0}
        )
        
        self.assertIn('dimensions', result)
        self.assertIn('confidence', result)
        self.assertIn('validation', result)
        
        # Check required dimension fields
        dims = result['dimensions']
        self.assertIn('foundation_length', dims)
        self.assertIn('foundation_width', dims)
        self.assertIn('stone_section_height', dims)
        self.assertIn('wood_section_height', dims)
        self.assertIn('num_wood_windows', dims)


if __name__ == '__main__':
    unittest.main()
