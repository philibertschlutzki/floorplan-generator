"""Dimensional extraction module for converting pixel measurements to real-world units.

This module:
- Converts pixel measurements to metric units
- Calculates building dimensions from detected features
- Estimates proportions and spacing
- Validates measurement consistency

Example:
    >>> from cv_modules import DimensionExtractor
    >>> extractor = DimensionExtractor(pixels_per_meter=100)
    >>> dimensions = extractor.extract(features, scale_info)
"""

import numpy as np
from typing import Dict, List, Tuple, Optional, Any
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class Dimensions:
    """Real-world dimensions in meters.
    
    Attributes:
        foundation_length: Length of foundation in meters
        foundation_width: Width of foundation in meters
        stone_section_height: Height of stone wall section
        wood_section_height: Height of wood wall section
        total_height: Total building height (excluding roof)
        confidence: Overall confidence score for measurements
    """
    foundation_length: float
    foundation_width: float
    stone_section_height: float
    wood_section_height: float
    total_height: float
    confidence: float = 0.0


class DimensionExtractor:
    """Extracts real-world dimensions from detected features.
    
    Converts pixel measurements to metric units and calculates
    building dimensions based on detected architectural features.
    
    Attributes:
        pixels_per_meter: Conversion factor from pixels to meters
        min_confidence: Minimum confidence threshold for measurements
        default_dimensions: Fallback dimensions if detection fails
    """
    
    def __init__(
        self,
        pixels_per_meter: float = 100.0,
        min_confidence: float = 0.3,
        default_dimensions: Optional[Dict[str, float]] = None
    ):
        """Initialize the DimensionExtractor.
        
        Args:
            pixels_per_meter: Scale conversion factor
            min_confidence: Minimum confidence threshold
            default_dimensions: Default dimensions to use as fallback
        """
        self.pixels_per_meter = pixels_per_meter
        self.min_confidence = min_confidence
        self.default_dimensions = default_dimensions or {
            "foundation_length": 8.5,
            "foundation_width": 7.0,
            "stone_section_height": 1.8,
            "wood_section_height": 2.5,
            "door_width": 1.5,
            "door_height": 1.5,
            "window_width": 1.0,
            "window_height": 1.0
        }
        logger.info(f"DimensionExtractor initialized with {pixels_per_meter} px/m")
    
    def pixels_to_meters(self, pixels: float) -> float:
        """Convert pixel measurement to meters.
        
        Args:
            pixels: Measurement in pixels
        
        Returns:
            Measurement in meters
        """
        return pixels / self.pixels_per_meter
    
    def extract_foundation_dimensions(
        self,
        image_shape: Tuple[int, int, int],
        wall_features: Dict[str, List[Dict]]
    ) -> Tuple[float, float, float]:
        """Extract foundation length and width from wall features.
        
        Args:
            image_shape: Shape of the processed image (h, w, c)
            wall_features: Detected wall features
        
        Returns:
            Tuple of (length, width, confidence)
        """
        height, width, _ = image_shape
        
        # Use image width as foundation length estimate
        # Assume building takes up ~80% of image width
        foundation_length = self.pixels_to_meters(width * 0.8)
        
        # Estimate width from depth perspective (assuming front view)
        # Use default ratio of 0.85 (width/length)
        foundation_width = foundation_length * 0.85
        
        confidence = 0.6  # Moderate confidence for estimated dimensions
        
        logger.debug(
            f"Extracted foundation: {foundation_length:.2f}m x {foundation_width:.2f}m"
        )
        return foundation_length, foundation_width, confidence
    
    def extract_wall_heights(
        self,
        wall_features: Dict[str, List[Dict]],
        image_height: int
    ) -> Tuple[float, float, float]:
        """Extract stone and wood section heights.
        
        Args:
            wall_features: Detected wall features with 'stone' and 'wood' sections
            image_height: Height of image in pixels
        
        Returns:
            Tuple of (stone_height, wood_height, confidence)
        """
        stone_height = 0.0
        wood_height = 0.0
        confidence = 0.5
        
        # Extract from detected features
        if wall_features.get("stone"):
            stone_bbox = wall_features["stone"][0]["bbox"]
            stone_height = self.pixels_to_meters(stone_bbox["height"])
            confidence += 0.2
        
        if wall_features.get("wood"):
            wood_bbox = wall_features["wood"][0]["bbox"]
            wood_height = self.pixels_to_meters(wood_bbox["height"])
            confidence += 0.2
        
        # Fallback to defaults if not detected
        if stone_height == 0.0:
            stone_height = self.default_dimensions["stone_section_height"]
            logger.warning("Using default stone section height")
        
        if wood_height == 0.0:
            wood_height = self.default_dimensions["wood_section_height"]
            logger.warning("Using default wood section height")
        
        confidence = min(confidence, 1.0)
        logger.debug(
            f"Extracted heights: stone={stone_height:.2f}m, wood={wood_height:.2f}m"
        )
        return stone_height, wood_height, confidence
    
    def extract_window_dimensions(
        self,
        windows: List[Dict[str, Any]]
    ) -> Tuple[float, float, int, float]:
        """Extract window dimensions and count.
        
        Args:
            windows: List of detected window features
        
        Returns:
            Tuple of (avg_width, avg_height, count, confidence)
        """
        if not windows:
            logger.warning("No windows detected, using defaults")
            return (
                self.default_dimensions["window_width"],
                self.default_dimensions["window_height"],
                3,
                0.0
            )
        
        widths = [self.pixels_to_meters(w["bbox"]["width"]) for w in windows]
        heights = [self.pixels_to_meters(w["bbox"]["height"]) for w in windows]
        
        avg_width = float(np.median(widths))
        avg_height = float(np.median(heights))
        count = len(windows)
        confidence = min(count / 5.0, 1.0)  # Higher confidence with more windows
        
        logger.debug(
            f"Extracted windows: {count} windows, {avg_width:.2f}m x {avg_height:.2f}m"
        )
        return avg_width, avg_height, count, confidence
    
    def extract_door_dimensions(
        self,
        doors: List[Dict[str, Any]],
        foundation_width: float
    ) -> Tuple[float, float, float, float]:
        """Extract door dimensions and position.
        
        Args:
            doors: List of detected door features
            foundation_width: Width of foundation for position calculation
        
        Returns:
            Tuple of (width, height, distance_from_edge, confidence)
        """
        if not doors:
            logger.warning("No doors detected, using defaults")
            return (
                self.default_dimensions["door_width"],
                self.default_dimensions["door_height"],
                0.5,  # Default distance from edge
                0.0
            )
        
        # Use first/largest door
        door = max(doors, key=lambda d: d["bbox"]["width"] * d["bbox"]["height"])
        bbox = door["bbox"]
        
        width = self.pixels_to_meters(bbox["width"])
        height = self.pixels_to_meters(bbox["height"])
        
        # Estimate distance from edge (simplified)
        distance_from_edge = self.pixels_to_meters(bbox["x"])
        
        # Clamp to reasonable range
        distance_from_edge = max(0.1, min(distance_from_edge, foundation_width * 0.3))
        
        confidence = 0.8
        
        logger.debug(
            f"Extracted door: {width:.2f}m x {height:.2f}m, offset={distance_from_edge:.2f}m"
        )
        return width, height, distance_from_edge, confidence
    
    def extract_roof_parameters(
        self,
        roof_info: Optional[Dict[str, Any]]
    ) -> Tuple[float, float, float]:
        """Extract roof pitch angle and overhang.
        
        Args:
            roof_info: Detected roof information
        
        Returns:
            Tuple of (pitch_angle, overhang, confidence)
        """
        if not roof_info:
            logger.warning("No roof detected, using default angle")
            return 45.0, 0.5, 0.0
        
        pitch_angle = roof_info.get("pitch_angle", 45.0)
        confidence = roof_info.get("confidence", 0.5)
        
        # Overhang is harder to detect, use reasonable default
        overhang = 0.5  # meters
        
        logger.debug(f"Extracted roof: pitch={pitch_angle:.1f}°, overhang={overhang:.2f}m")
        return pitch_angle, overhang, confidence
    
    def validate_dimensions(
        self,
        dimensions: Dict[str, Any]
    ) -> Tuple[bool, List[str]]:
        """Validate extracted dimensions for physical plausibility.
        
        Args:
            dimensions: Dictionary of extracted dimensions
        
        Returns:
            Tuple of (is_valid, list_of_warnings)
        """
        warnings = []
        is_valid = True
        
        # Check foundation dimensions
        if dimensions["foundation_length"] < 3.0 or dimensions["foundation_length"] > 20.0:
            warnings.append(
                f"Foundation length {dimensions['foundation_length']:.2f}m is unusual"
            )
        
        if dimensions["foundation_width"] < 3.0 or dimensions["foundation_width"] > 15.0:
            warnings.append(
                f"Foundation width {dimensions['foundation_width']:.2f}m is unusual"
            )
        
        # Check wall heights
        total_wall_height = (
            dimensions["stone_section_height"] + dimensions["wood_section_height"]
        )
        if total_wall_height < 2.0 or total_wall_height > 8.0:
            warnings.append(f"Total wall height {total_wall_height:.2f}m is unusual")
        
        # Check door fits in wall
        if dimensions["door_height"] > dimensions["stone_section_height"]:
            warnings.append(
                "Door height exceeds stone section height - may span both sections"
            )
        
        # Check window size
        if dimensions["wood_window_width"] > 3.0 or dimensions["wood_window_height"] > 3.0:
            warnings.append("Window dimensions are unusually large")
        
        # Check roof angle
        if dimensions["roof_pitch_angle"] < 15.0 or dimensions["roof_pitch_angle"] > 75.0:
            warnings.append(
                f"Roof pitch {dimensions['roof_pitch_angle']:.1f}° is unusual"
            )
        
        if warnings:
            logger.warning(f"Validation warnings: {warnings}")
        
        return is_valid, warnings
    
    def extract(
        self,
        detections: Dict[str, Any],
        image_shape: Tuple[int, int, int],
        scale_info: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Complete dimension extraction pipeline.
        
        Args:
            detections: Feature detection results from FeatureDetector
            image_shape: Shape of processed image (h, w, c)
            scale_info: Optional scale information from preprocessing
        
        Returns:
            Dictionary containing all extracted dimensions and metadata
        """
        logger.info("Starting dimension extraction")
        
        # Update scale if provided
        if scale_info and "pixels_per_meter" in scale_info:
            self.pixels_per_meter = scale_info["pixels_per_meter"]
            logger.info(f"Using scale: {self.pixels_per_meter} px/m")
        
        # Extract all dimensions
        foundation_length, foundation_width, found_conf = \
            self.extract_foundation_dimensions(image_shape, detections["walls"])
        
        stone_height, wood_height, wall_conf = \
            self.extract_wall_heights(detections["walls"], image_shape[0])
        
        window_width, window_height, num_windows, window_conf = \
            self.extract_window_dimensions(detections["windows"])
        
        door_width, door_height, door_offset, door_conf = \
            self.extract_door_dimensions(detections["doors"], foundation_width)
        
        roof_angle, roof_overhang, roof_conf = \
            self.extract_roof_parameters(detections["roof"])
        
        # Calculate overall confidence
        overall_confidence = np.mean([
            found_conf, wall_conf, window_conf, door_conf, roof_conf
        ])
        
        dimensions = {
            "foundation_length": round(foundation_length, 1),
            "foundation_width": round(foundation_width, 1),
            "stone_section_height": round(stone_height, 1),
            "stone_wall_thickness": 1.0,  # Difficult to detect from 2D, use default
            "wood_section_height": round(wood_height, 1),
            "log_diameter": 0.2,  # Default, requires close-up to detect
            "door_width": round(door_width, 1),
            "door_height": round(door_height, 1),
            "door_distance_from_edge": round(door_offset, 1),
            "wood_window_width": round(window_width, 1),
            "wood_window_height": round(window_height, 1),
            "num_wood_windows": num_windows,
            "roof_pitch_angle": round(roof_angle, 1),
            "roof_overhang": round(roof_overhang, 1),
            "roof_material": "rotes Blech",  # Cannot detect from image
            "porch_width": 0,  # TODO: Implement porch detection
            "porch_depth": 0,
            "porch_height": 0,
            "stone_finish": "rauer Naturstein",
            "color_description": "grauer Stein"
        }
        
        # Validate dimensions
        is_valid, warnings = self.validate_dimensions(dimensions)
        
        result = {
            "dimensions": dimensions,
            "confidence": round(overall_confidence, 2),
            "confidence_details": {
                "foundation": round(found_conf, 2),
                "walls": round(wall_conf, 2),
                "windows": round(window_conf, 2),
                "door": round(door_conf, 2),
                "roof": round(roof_conf, 2)
            },
            "validation": {
                "is_valid": is_valid,
                "warnings": warnings
            },
            "scale_used": self.pixels_per_meter
        }
        
        logger.info(
            f"Dimension extraction complete. Overall confidence: {overall_confidence:.2f}"
        )
        return result
