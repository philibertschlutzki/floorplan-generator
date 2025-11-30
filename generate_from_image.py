#!/usr/bin/env python3
"""
This script provides the core functionalities for image processing and feature detection.
It is intended to be used as a module by the main application orchestrator.
"""

import logging
import sys
from typing import Optional

try:
    from cv_modules import (
        ImagePreprocessor,
        FeatureDetector,
        ConfigGenerator
    )
except ImportError:
    print("Error: cv_modules not found. Make sure you've installed requirements:")
    print("  pip install -r requirements.txt")
    sys.exit(1)

def process_image(
    image_path: str,
    apply_perspective: bool = True,
    manual_points=None,
    apply_enhancement: bool = True,
    logger: Optional[logging.Logger] = None
) -> tuple:
    """
    Process image through preprocessing pipeline.
    
    Args:
        image_path: Path to input image
        apply_perspective: Whether to apply perspective correction
        manual_points: Optional manual points for perspective correction
        apply_enhancement: Whether to apply image enhancement
        logger: Logger instance
    
    Returns:
        Tuple of (processed_image, metadata)
    """
    if logger:
        logger.info(f"Processing image: {image_path}")
    
    preprocessor = ImagePreprocessor()
    
    processed_img, metadata = preprocessor.process(
        image_path,
        apply_perspective=apply_perspective,
        manual_points=manual_points,
        apply_enhancement=apply_enhancement,
        apply_denoising=True
    )
    
    if logger:
        logger.info(f"Preprocessing complete: {metadata['steps_applied']}")
    
    return processed_img, metadata


def detect_features(
    image,
    logger: Optional[logging.Logger] = None
) -> dict:
    """
    Detect architectural features in image.
    
    Args:
        image: Preprocessed image
        logger: Logger instance
    
    Returns:
        Dictionary of detected features
    """
    if logger:
        logger.info("Starting feature detection...")
    
    detector = FeatureDetector()
    detections = detector.detect_all(image)
    
    if logger:
        summary = detections['summary']
        logger.info(
            f"Detected: {summary['num_windows']} windows, "
            f"{summary['num_doors']} doors, "
            f"roof: {summary['has_roof']}"
        )
    
    return detections


def generate_config(
    dimensions_result: dict,
    building_type: str,
    logger: Optional[logging.Logger] = None
) -> dict:
    """
    Generate JSON configuration from extracted dimensions.
    
    Args:
        dimensions_result: Result from dimension extraction
        building_type: Type of building
        logger: Logger instance
    
    Returns:
        Complete JSON configuration
    """
    if logger:
        logger.info("Generating JSON configuration...")
    
    generator = ConfigGenerator(building_type=building_type)
    
    metadata = {
        'extraction_confidence': dimensions_result['confidence'],
        'confidence_details': dimensions_result.get('confidence_details', {}),
        'validation_warnings': dimensions_result['validation']['warnings'],
        'scale_used': dimensions_result['scale_used'],
        'generation_method': 'interactive'
    }
    
    config = generator.generate(
        dimensions=dimensions_result['dimensions'],
        building_type=building_type,
        metadata=metadata
    )
    
    if logger:
        logger.info("Configuration generated successfully")
    
    return config


def save_visualization(
    image,
    detections: dict,
    output_path: str,
    logger: Optional[logging.Logger] = None
):
    """
    Save visualization of detected features.
    
    Args:
        image: Original/processed image
        detections: Feature detection results
        output_path: Path to save visualization
        logger: Logger instance
    """
    if logger:
        logger.info(f"Saving visualization to {output_path}")
    
    detector = FeatureDetector()
    detector.visualize_detections(image, detections, output_path)
