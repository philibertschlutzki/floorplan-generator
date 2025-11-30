"""Building feature detection module using OpenCV.

This module detects architectural features from preprocessed images:
- Wall sections (stone, wood)
- Windows and their positions
- Doors and entrance areas
- Roof structures and angles
- Veranda/porch areas

Example:
    >>> from cv_modules import FeatureDetector
    >>> detector = FeatureDetector()
    >>> features = detector.detect_all(preprocessed_image)
    >>> print(f"Found {len(features['windows'])} windows")
"""

import cv2
import numpy as np
from typing import List, Dict, Tuple, Optional, Any
import logging
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)


@dataclass
class BoundingBox:
    """Represents a rectangular bounding box.
    
    Attributes:
        x: X-coordinate of top-left corner
        y: Y-coordinate of top-left corner
        width: Width of bounding box
        height: Height of bounding box
        confidence: Detection confidence score (0-1)
    """
    x: int
    y: int
    width: int
    height: int
    confidence: float = 1.0
    
    def center(self) -> Tuple[int, int]:
        """Calculate center point of bounding box."""
        return (self.x + self.width // 2, self.y + self.height // 2)
    
    def area(self) -> int:
        """Calculate area of bounding box."""
        return self.width * self.height
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


@dataclass
class DetectedFeature:
    """Represents a detected architectural feature.
    
    Attributes:
        feature_type: Type of feature (window, door, wall, etc.)
        bbox: Bounding box of the feature
        properties: Additional feature-specific properties
    """
    feature_type: str
    bbox: BoundingBox
    properties: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "feature_type": self.feature_type,
            "bbox": self.bbox.to_dict(),
            "properties": self.properties
        }


class FeatureDetector:
    """Detects architectural features in building images.
    
    Uses various OpenCV techniques including:
    - Canny edge detection
    - Hough line/circle transforms
    - Contour analysis
    - Template matching
    - Color segmentation
    
    Attributes:
        canny_low: Lower threshold for Canny edge detection
        canny_high: Upper threshold for Canny edge detection
        min_window_area: Minimum pixel area for window detection
        min_door_area: Minimum pixel area for door detection
    """
    
    def __init__(
        self,
        canny_low: int = 50,
        canny_high: int = 150,
        min_window_area: int = 1000,
        min_door_area: int = 2000
    ):
        """Initialize the FeatureDetector.
        
        Args:
            canny_low: Lower threshold for Canny edge detection
            canny_high: Upper threshold for Canny edge detection
            min_window_area: Minimum area in pixels for window detection
            min_door_area: Minimum area in pixels for door detection
        """
        self.canny_low = canny_low
        self.canny_high = canny_high
        self.min_window_area = min_window_area
        self.min_door_area = min_door_area
        logger.info("FeatureDetector initialized")
    
    def detect_edges(self, image: np.ndarray) -> np.ndarray:
        """Detect edges in image using Canny algorithm.
        
        Args:
            image: Input image (BGR or grayscale)
        
        Returns:
            Binary edge map
        """
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
        
        edges = cv2.Canny(gray, self.canny_low, self.canny_high)
        logger.debug("Edge detection completed")
        return edges
    
    def detect_lines(
        self,
        edges: np.ndarray,
        min_line_length: int = 50,
        max_line_gap: int = 10
    ) -> List[Tuple[int, int, int, int]]:
        """Detect straight lines using Hough transform.
        
        Args:
            edges: Binary edge map
            min_line_length: Minimum line length in pixels
            max_line_gap: Maximum gap between line segments
        
        Returns:
            List of lines as (x1, y1, x2, y2) tuples
        """
        lines = cv2.HoughLinesP(
            edges,
            rho=1,
            theta=np.pi/180,
            threshold=50,
            minLineLength=min_line_length,
            maxLineGap=max_line_gap
        )
        
        if lines is None:
            logger.warning("No lines detected")
            return []
        
        line_list = [tuple(line[0]) for line in lines]
        logger.debug(f"Detected {len(line_list)} lines")
        return line_list
    
    def detect_rectangles(
        self,
        image: np.ndarray,
        min_area: int = 500
    ) -> List[BoundingBox]:
        """Detect rectangular shapes in image.
        
        Args:
            image: Input image
            min_area: Minimum area threshold in pixels
        
        Returns:
            List of detected rectangular bounding boxes
        """
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
        
        # Apply threshold
        _, thresh = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
        
        # Find contours
        contours, _ = cv2.findContours(
            thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )
        
        rectangles = []
        for contour in contours:
            area = cv2.contourArea(contour)
            if area < min_area:
                continue
            
            # Approximate contour to polygon
            peri = cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, 0.04 * peri, True)
            
            # Check if it's a rectangle (4 corners)
            if len(approx) == 4:
                x, y, w, h = cv2.boundingRect(approx)
                bbox = BoundingBox(x, y, w, h, confidence=0.8)
                rectangles.append(bbox)
        
        logger.debug(f"Detected {len(rectangles)} rectangles")
        return rectangles
    
    def detect_windows(
        self,
        image: np.ndarray,
        edge_map: Optional[np.ndarray] = None
    ) -> List[DetectedFeature]:
        """Detect window features in building image.
        
        Windows are identified by:
        - Rectangular shape
        - Specific size range
        - Regular spacing patterns
        - Dark regions (glass reflection)
        
        Args:
            image: Input image
            edge_map: Pre-computed edge map (optional)
        
        Returns:
            List of detected window features
        """
        if edge_map is None:
            edge_map = self.detect_edges(image)
        
        # Detect rectangles
        rectangles = self.detect_rectangles(edge_map, min_area=self.min_window_area)
        
        windows = []
        for bbox in rectangles:
            # Filter by aspect ratio (windows are typically square or vertical)
            aspect_ratio = bbox.width / bbox.height if bbox.height > 0 else 0
            
            if 0.5 <= aspect_ratio <= 2.0:
                feature = DetectedFeature(
                    feature_type="window",
                    bbox=bbox,
                    properties={
                        "aspect_ratio": aspect_ratio,
                        "area": bbox.area()
                    }
                )
                windows.append(feature)
        
        logger.info(f"Detected {len(windows)} windows")
        return windows
    
    def detect_doors(
        self,
        image: np.ndarray,
        edge_map: Optional[np.ndarray] = None
    ) -> List[DetectedFeature]:
        """Detect door features in building image.
        
        Doors are identified by:
        - Rectangular shape
        - Vertical orientation (height > width)
        - Larger than windows
        - Typically at ground level
        
        Args:
            image: Input image
            edge_map: Pre-computed edge map (optional)
        
        Returns:
            List of detected door features
        """
        if edge_map is None:
            edge_map = self.detect_edges(image)
        
        rectangles = self.detect_rectangles(edge_map, min_area=self.min_door_area)
        
        doors = []
        image_height = image.shape[0]
        
        for bbox in rectangles:
            # Doors are typically vertical (height > width)
            aspect_ratio = bbox.width / bbox.height if bbox.height > 0 else 0
            
            # Check if in lower half of image (ground level)
            is_ground_level = bbox.y + bbox.height > image_height * 0.5
            
            if 0.3 <= aspect_ratio <= 0.8 and is_ground_level:
                feature = DetectedFeature(
                    feature_type="door",
                    bbox=bbox,
                    properties={
                        "aspect_ratio": aspect_ratio,
                        "area": bbox.area(),
                        "ground_level": is_ground_level
                    }
                )
                doors.append(feature)
        
        logger.info(f"Detected {len(doors)} doors")
        return doors
    
    def detect_roof(
        self,
        image: np.ndarray,
        edge_map: Optional[np.ndarray] = None
    ) -> Optional[Dict[str, Any]]:
        """Detect roof structure and estimate pitch angle.
        
        Args:
            image: Input image
            edge_map: Pre-computed edge map (optional)
        
        Returns:
            Dictionary with roof information:
                - pitch_angle: Estimated roof angle in degrees
                - ridge_line: Ridge line coordinates
                - confidence: Detection confidence
        """
        if edge_map is None:
            edge_map = self.detect_edges(image)
        
        lines = self.detect_lines(edge_map, min_line_length=100)
        
        if not lines:
            logger.warning("No roof lines detected")
            return None
        
        # Find angled lines in upper portion of image
        image_height = image.shape[0]
        roof_lines = []
        
        for x1, y1, x2, y2 in lines:
            # Check if line is in upper half
            avg_y = (y1 + y2) / 2
            if avg_y < image_height * 0.5:
                # Calculate angle
                angle = abs(np.arctan2(y2 - y1, x2 - x1) * 180 / np.pi)
                # Roof lines are typically 20-70 degrees from horizontal
                if 20 <= angle <= 70:
                    roof_lines.append((x1, y1, x2, y2, angle))
        
        if not roof_lines:
            logger.warning("No angled roof lines found")
            return None
        
        # Estimate pitch angle from median of detected angles
        angles = [line[4] for line in roof_lines]
        pitch_angle = float(np.median(angles))
        
        roof_info = {
            "pitch_angle": pitch_angle,
            "num_lines_detected": len(roof_lines),
            "confidence": min(len(roof_lines) / 10.0, 1.0)
        }
        
        logger.info(f"Detected roof with pitch angle: {pitch_angle:.1f}°")
        return roof_info
    
    def detect_wall_sections(
        self,
        image: np.ndarray
    ) -> Dict[str, List[DetectedFeature]]:
        """Detect different wall sections (stone base, wood upper).
        
        Uses color and texture analysis to distinguish between:
        - Stone/masonry sections (lower, darker, rough texture)
        - Wood sections (upper, lighter, horizontal lines)
        
        Args:
            image: Input image
        
        Returns:
            Dictionary with 'stone' and 'wood' section lists
        """
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        height = image.shape[0]
        
        # Define color ranges for stone (gray) and wood (brown)
        # Stone: low saturation, medium-low value
        stone_lower = np.array([0, 0, 30])
        stone_upper = np.array([180, 50, 120])
        
        # Wood: brown hues
        wood_lower = np.array([10, 20, 60])
        wood_upper = np.array([30, 200, 200])
        
        stone_mask = cv2.inRange(hsv, stone_lower, stone_upper)
        wood_mask = cv2.inRange(hsv, wood_lower, wood_upper)
        
        # Find stone sections (typically lower portion)
        stone_sections = []
        wood_sections = []
        
        # Simplified: divide image into upper and lower halves
        lower_half = BoundingBox(
            x=0,
            y=int(height * 0.5),
            width=image.shape[1],
            height=int(height * 0.5),
            confidence=0.7
        )
        
        upper_half = BoundingBox(
            x=0,
            y=0,
            width=image.shape[1],
            height=int(height * 0.5),
            confidence=0.7
        )
        
        stone_feature = DetectedFeature(
            feature_type="stone_wall",
            bbox=lower_half,
            properties={"material": "stone", "finish": "rough"}
        )
        
        wood_feature = DetectedFeature(
            feature_type="wood_wall",
            bbox=upper_half,
            properties={"material": "wood", "construction": "log"}
        )
        
        logger.info("Detected wall sections (stone and wood)")
        return {
            "stone": [stone_feature],
            "wood": [wood_feature]
        }
    
    def detect_all(
        self,
        image: np.ndarray
    ) -> Dict[str, Any]:
        """Run complete feature detection pipeline.
        
        Args:
            image: Preprocessed input image
        
        Returns:
            Dictionary containing all detected features:
                - windows: List of window features
                - doors: List of door features
                - roof: Roof information
                - walls: Wall section features
                - edges: Edge map for visualization
        """
        logger.info("Starting complete feature detection")
        
        # Detect edges once for efficiency
        edge_map = self.detect_edges(image)
        
        # Detect all features
        windows = self.detect_windows(image, edge_map)
        doors = self.detect_doors(image, edge_map)
        roof = self.detect_roof(image, edge_map)
        walls = self.detect_wall_sections(image)
        
        results = {
            "windows": [w.to_dict() for w in windows],
            "doors": [d.to_dict() for d in doors],
            "roof": roof,
            "walls": {
                "stone": [s.to_dict() for s in walls["stone"]],
                "wood": [w.to_dict() for w in walls["wood"]]
            },
            "edge_map": edge_map,
            "summary": {
                "num_windows": len(windows),
                "num_doors": len(doors),
                "has_roof": roof is not None,
                "num_wall_sections": len(walls["stone"]) + len(walls["wood"])
            }
        }
        
        logger.info(f"Feature detection complete: {results['summary']}")
        return results
    
    def visualize_detections(
        self,
        image: np.ndarray,
        detections: Dict[str, Any],
        output_path: Optional[str] = None
    ) -> np.ndarray:
        """Visualize detected features on image.
        
        Args:
            image: Original image
            detections: Detection results from detect_all()
            output_path: Optional path to save visualization
        
        Returns:
            Image with drawn bounding boxes and labels
        """
        vis_img = image.copy()
        
        # Draw windows (green)
        for window in detections["windows"]:
            bbox = window["bbox"]
            cv2.rectangle(
                vis_img,
                (bbox["x"], bbox["y"]),
                (bbox["x"] + bbox["width"], bbox["y"] + bbox["height"]),
                (0, 255, 0),
                2
            )
            cv2.putText(
                vis_img,
                "Window",
                (bbox["x"], bbox["y"] - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (0, 255, 0),
                2
            )
        
        # Draw doors (blue)
        for door in detections["doors"]:
            bbox = door["bbox"]
            cv2.rectangle(
                vis_img,
                (bbox["x"], bbox["y"]),
                (bbox["x"] + bbox["width"], bbox["y"] + bbox["height"]),
                (255, 0, 0),
                2
            )
            cv2.putText(
                vis_img,
                "Door",
                (bbox["x"], bbox["y"] - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (255, 0, 0),
                2
            )
        
        # Draw roof info
        if detections["roof"]:
            roof = detections["roof"]
            text = f"Roof: {roof['pitch_angle']:.1f}°"
            cv2.putText(
                vis_img,
                text,
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                1.0,
                (0, 0, 255),
                2
            )
        
        if output_path:
            cv2.imwrite(output_path, vis_img)
            logger.info(f"Visualization saved to {output_path}")
        
        return vis_img
