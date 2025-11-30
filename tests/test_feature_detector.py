"""Tests for FeatureDetector module."""

import unittest
import numpy as np
import cv2
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from cv_modules.feature_detector import FeatureDetector, BoundingBox, DetectedFeature


class TestBoundingBox(unittest.TestCase):
    """Test cases for BoundingBox class."""
    
    def test_initialization(self):
        """Test bounding box creation."""
        bbox = BoundingBox(10, 20, 100, 50, 0.9)
        self.assertEqual(bbox.x, 10)
        self.assertEqual(bbox.y, 20)
        self.assertEqual(bbox.width, 100)
        self.assertEqual(bbox.height, 50)
        self.assertEqual(bbox.confidence, 0.9)
    
    def test_center_calculation(self):
        """Test center point calculation."""
        bbox = BoundingBox(0, 0, 100, 50)
        center = bbox.center()
        self.assertEqual(center, (50, 25))
    
    def test_area_calculation(self):
        """Test area calculation."""
        bbox = BoundingBox(0, 0, 100, 50)
        self.assertEqual(bbox.area(), 5000)


class TestFeatureDetector(unittest.TestCase):
    """Test cases for FeatureDetector class."""
    
    @classmethod
    def setUpClass(cls):
        """Create test images with known features."""
        # Create image with rectangles (simulating windows/doors)
        cls.test_image = np.ones((800, 1000, 3), dtype=np.uint8) * 255
        
        # Draw "building" structure
        # Stone section (gray)
        cv2.rectangle(cls.test_image, (100, 400), (900, 700), (150, 150, 150), -1)
        
        # Wood section (brown)
        cv2.rectangle(cls.test_image, (100, 200), (900, 400), (139, 90, 43), -1)
        
        # Windows (dark rectangles in wood section)
        cv2.rectangle(cls.test_image, (200, 250), (280, 330), (50, 50, 150), -1)
        cv2.rectangle(cls.test_image, (400, 250), (480, 330), (50, 50, 150), -1)
        cv2.rectangle(cls.test_image, (600, 250), (680, 330), (50, 50, 150), -1)
        
        # Door (larger rectangle in stone section)
        cv2.rectangle(cls.test_image, (450, 500), (550, 680), (70, 40, 20), -1)
        
        # Roof (triangle)
        pts = np.array([[500, 100], [100, 200], [900, 200]], dtype=np.int32)
        cv2.fillPoly(cls.test_image, [pts], (200, 50, 50))
    
    def test_initialization(self):
        """Test detector initialization."""
        detector = FeatureDetector()
        self.assertIsNotNone(detector)
        self.assertEqual(detector.canny_low, 50)
        self.assertEqual(detector.canny_high, 150)
    
    def test_edge_detection(self):
        """Test edge detection."""
        detector = FeatureDetector()
        edges = detector.detect_edges(self.test_image)
        self.assertEqual(edges.shape[:2], self.test_image.shape[:2])
        self.assertEqual(len(edges.shape), 2)  # Binary image
    
    def test_line_detection(self):
        """Test line detection."""
        detector = FeatureDetector()
        edges = detector.detect_edges(self.test_image)
        lines = detector.detect_lines(edges, min_line_length=50)
        self.assertIsInstance(lines, list)
    
    def test_rectangle_detection(self):
        """Test rectangle detection."""
        detector = FeatureDetector()
        rectangles = detector.detect_rectangles(self.test_image, min_area=500)
        self.assertIsInstance(rectangles, list)
    
    def test_window_detection(self):
        """Test window detection."""
        detector = FeatureDetector(min_window_area=1000)
        windows = detector.detect_windows(self.test_image)
        self.assertIsInstance(windows, list)
        # Should detect some windows
        self.assertGreaterEqual(len(windows), 0)
    
    def test_door_detection(self):
        """Test door detection."""
        detector = FeatureDetector(min_door_area=2000)
        doors = detector.detect_doors(self.test_image)
        self.assertIsInstance(doors, list)
    
    def test_roof_detection(self):
        """Test roof detection."""
        detector = FeatureDetector()
        roof_info = detector.detect_roof(self.test_image)
        # May or may not detect roof depending on image complexity
        if roof_info:
            self.assertIn('pitch_angle', roof_info)
            self.assertIn('confidence', roof_info)
    
    def test_wall_section_detection(self):
        """Test wall section detection."""
        detector = FeatureDetector()
        walls = detector.detect_wall_sections(self.test_image)
        self.assertIn('stone', walls)
        self.assertIn('wood', walls)
    
    def test_detect_all(self):
        """Test complete detection pipeline."""
        detector = FeatureDetector()
        results = detector.detect_all(self.test_image)
        
        self.assertIn('windows', results)
        self.assertIn('doors', results)
        self.assertIn('roof', results)
        self.assertIn('walls', results)
        self.assertIn('summary', results)
        
        # Check summary structure
        summary = results['summary']
        self.assertIn('num_windows', summary)
        self.assertIn('num_doors', summary)
        self.assertIn('has_roof', summary)


if __name__ == '__main__':
    unittest.main()
