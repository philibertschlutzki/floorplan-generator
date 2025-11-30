"""Tests for ConfigGenerator module."""

import unittest
import json
import tempfile
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from cv_modules.config_generator import ConfigGenerator


class TestConfigGenerator(unittest.TestCase):
    """Test cases for ConfigGenerator class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.generator = ConfigGenerator()
        self.test_dir = Path(tempfile.mkdtemp())
        
        self.mock_dimensions = {
            'foundation_length': 8.5,
            'foundation_width': 7.0,
            'stone_section_height': 1.8,
            'stone_wall_thickness': 1.0,
            'wood_section_height': 2.5,
            'log_diameter': 0.2,
            'door_width': 1.5,
            'door_height': 1.5,
            'door_distance_from_edge': 0.5,
            'wood_window_width': 1.0,
            'wood_window_height': 1.0,
            'num_wood_windows': 3,
            'roof_pitch_angle': 45.0,
            'roof_overhang': 0.5,
            'roof_material': 'rotes Blech',
            'porch_width': 0,
            'porch_depth': 0,
            'porch_height': 0,
            'stone_finish': 'rauer Naturstein',
            'color_description': 'grauer Stein'
        }
    
    def test_initialization(self):
        """Test generator initialization."""
        self.assertEqual(self.generator.default_scale, "1:50")
        self.assertEqual(self.generator.default_unit, "meters")
        self.assertEqual(self.generator.building_type, "Alpine Sennhütte")
    
    def test_generate_config(self):
        """Test configuration generation."""
        config = self.generator.generate(self.mock_dimensions)
        
        self.assertIn('timestamp', config)
        self.assertIn('building_type', config)
        self.assertIn('dimensions', config)
        self.assertIn('scale', config)
        self.assertIn('unit', config)
        
        self.assertEqual(config['building_type'], 'Alpine Sennhütte')
        self.assertEqual(config['scale'], '1:50')
        self.assertEqual(config['unit'], 'meters')
    
    def test_generate_with_metadata(self):
        """Test configuration generation with metadata."""
        metadata = {
            'extraction_confidence': 0.85,
            'generation_method': 'computer_vision'
        }
        
        config = self.generator.generate(
            self.mock_dimensions,
            metadata=metadata
        )
        
        self.assertIn('metadata', config)
        self.assertEqual(config['metadata']['extraction_confidence'], 0.85)
    
    def test_save_config(self):
        """Test saving configuration to file."""
        config = self.generator.generate(self.mock_dimensions)
        output_path = self.test_dir / "test_config.json"
        
        success = self.generator.save_config(config, str(output_path))
        
        self.assertTrue(success)
        self.assertTrue(output_path.exists())
        
        # Verify file content
        with open(output_path, 'r') as f:
            loaded_config = json.load(f)
        
        self.assertEqual(loaded_config['building_type'], config['building_type'])
    
    def test_load_config(self):
        """Test loading configuration from file."""
        config = self.generator.generate(self.mock_dimensions)
        output_path = self.test_dir / "test_config.json"
        
        self.generator.save_config(config, str(output_path))
        loaded_config = self.generator.load_config(str(output_path))
        
        self.assertIsNotNone(loaded_config)
        self.assertEqual(loaded_config['building_type'], config['building_type'])
    
    def test_validate_valid_config(self):
        """Test validation of valid configuration."""
        config = self.generator.generate(self.mock_dimensions)
        is_valid, errors = self.generator.validate_config(config)
        
        self.assertTrue(is_valid)
        self.assertEqual(len(errors), 0)
    
    def test_validate_invalid_config(self):
        """Test validation of invalid configuration."""
        invalid_config = {
            'timestamp': '2025-01-01T00:00:00',
            # Missing required fields
        }
        
        is_valid, errors = self.generator.validate_config(invalid_config)
        
        self.assertFalse(is_valid)
        self.assertGreater(len(errors), 0)


if __name__ == '__main__':
    unittest.main()
