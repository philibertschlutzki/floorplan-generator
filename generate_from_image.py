#!/usr/bin/env python3
"""Main orchestrator script for image-to-config generation.

This script coordinates the complete pipeline:
1. Load and preprocess building image
2. Detect architectural features using Computer Vision
3. Extract dimensional measurements
4. Generate JSON configuration file
5. Validate output

Usage:
    python generate_from_image.py --input building.jpg --output config.json
    python generate_from_image.py --input building.jpg --output config.json --scale 120 --visualize

Example:
    # Basic usage
    python generate_from_image.py -i test_inputs/example_building.png -o configs/generated.json
    
    # With custom scale and visualization
    python generate_from_image.py -i image.jpg -o config.json --scale 100 --visualize --debug
"""

import argparse
import logging
import sys
from pathlib import Path
import json
from typing import Optional

try:
    from cv_modules import (
        ImagePreprocessor,
        FeatureDetector,
        DimensionExtractor,
        ConfigGenerator,
        InteractiveScaler
    )
except ImportError:
    print("Error: cv_modules not found. Make sure you've installed requirements:")
    print("  pip install -r requirements.txt")
    sys.exit(1)


def setup_logging(debug: bool = False) -> logging.Logger:
    """Configure logging based on debug flag.
    
    Args:
        debug: Enable debug-level logging
    
    Returns:
        Configured logger instance
    """
    level = logging.DEBUG if debug else logging.INFO
    
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('logs/image_to_config.log', mode='a')
        ]
    )
    
    return logging.getLogger(__name__)


def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments.
    
    Returns:
        Parsed arguments namespace
    """
    parser = argparse.ArgumentParser(
        description='Generate building configuration from image using Computer Vision',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s -i building.jpg -o config.json
  %(prog)s -i photo.png -o output.json --scale 150 --visualize
  %(prog)s -i sketch.jpg -o result.json --debug --no-perspective
        """
    )
    
    parser.add_argument(
        '-i', '--input',
        required=True,
        type=str,
        help='Path to input building image'
    )
    
    parser.add_argument(
        '-o', '--output',
        required=True,
        type=str,
        help='Path to output JSON configuration file'
    )
    
    parser.add_argument(
        '--scale',
        type=float,
        default=None,
        help='Pixels per meter (if known). Auto-detected if not provided.'
    )
    
    parser.add_argument(
        '--visualize',
        action='store_true',
        help='Save visualization of detected features'
    )
    
    parser.add_argument(
        '--no-perspective',
        action='store_true',
        help='Skip perspective correction'
    )
    
    parser.add_argument(
        '--no-enhancement',
        action='store_true',
        help='Skip image enhancement'
    )
    
    parser.add_argument(
        '--building-type',
        type=str,
        default='Alpine Sennhütte',
        help='Type of building (default: Alpine Sennhütte)'
    )
    
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug logging'
    )

    parser.add_argument(
        '--interactive-scale',
        action='store_true',
        help='Use interactive tool to define scale'
    )
    
    return parser.parse_args()


def process_image(
    image_path: str,
    apply_perspective: bool = True,
    apply_enhancement: bool = True,
    logger: Optional[logging.Logger] = None
) -> tuple:
    """Process image through preprocessing pipeline.
    
    Args:
        image_path: Path to input image
        apply_perspective: Whether to apply perspective correction
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
    """Detect architectural features in image.
    
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


def extract_dimensions(
    detections: dict,
    image_shape: tuple,
    scale_info: Optional[dict] = None,
    custom_scale: Optional[float] = None,
    logger: Optional[logging.Logger] = None
) -> dict:
    """Extract real-world dimensions from detections.
    
    Args:
        detections: Feature detection results
        image_shape: Shape of processed image
        scale_info: Scale information from preprocessing
        custom_scale: User-provided scale override
        logger: Logger instance
    
    Returns:
        Dictionary with extracted dimensions and metadata
    """
    if logger:
        logger.info("Extracting dimensions...")
    
    # Use custom scale if provided
    if custom_scale:
        scale_info = {'pixels_per_meter': custom_scale}
        if logger:
            logger.info(f"Using custom scale: {custom_scale} px/m")
    
    extractor = DimensionExtractor(
        pixels_per_meter=scale_info.get('pixels_per_meter', 100.0) if scale_info else 100.0
    )
    
    result = extractor.extract(detections, image_shape, scale_info)
    
    if logger:
        logger.info(f"Extraction complete. Confidence: {result['confidence']:.2f}")
        if result['validation']['warnings']:
            logger.warning(f"Validation warnings: {result['validation']['warnings']}")
    
    return result


def generate_config(
    dimensions_result: dict,
    building_type: str,
    logger: Optional[logging.Logger] = None
) -> dict:
    """Generate JSON configuration from extracted dimensions.
    
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
        'confidence_details': dimensions_result['confidence_details'],
        'validation_warnings': dimensions_result['validation']['warnings'],
        'scale_used': dimensions_result['scale_used'],
        'generation_method': 'computer_vision'
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
    """Save visualization of detected features.
    
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


def main():
    """Main execution function."""
    args = parse_arguments()
    
    # Setup logging
    Path('logs').mkdir(exist_ok=True)
    logger = setup_logging(args.debug)
    
    logger.info("="*60)
    logger.info("Floorplan Generator - Image to Config Pipeline")
    logger.info("="*60)
    
    try:
        # Validate input
        input_path = Path(args.input)
        if not input_path.exists():
            logger.error(f"Input file not found: {args.input}")
            sys.exit(1)
        
        # Create output directory
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Pipeline execution
        logger.info("Step 1/5: Image Preprocessing")
        processed_img, metadata = process_image(
            str(input_path),
            apply_perspective=not args.no_perspective,
            apply_enhancement=not args.no_enhancement,
            logger=logger
        )
        
        logger.info("Step 2/5: Feature Detection")
        detections = detect_features(processed_img, logger)
        
        # Determine scale
        custom_scale = args.scale
        if args.interactive_scale:
            logger.info("Starting interactive scaling...")
            scaler = InteractiveScaler(str(input_path))
            interactive_scale = scaler.get_scale()
            if interactive_scale:
                custom_scale = interactive_scale
                logger.info(f"Using interactively defined scale: {custom_scale:.2f} px/m")
            else:
                logger.warning("Interactive scaling cancelled. Falling back to default.")

        logger.info("Step 3/5: Dimension Extraction")
        dimensions_result = extract_dimensions(
            detections,
            processed_img.shape,
            metadata.get('scale'),
            custom_scale,
            logger
        )
        
        logger.info("Step 4/5: Configuration Generation")
        config = generate_config(
            dimensions_result,
            args.building_type,
            logger
        )
        
        logger.info("Step 5/5: Saving Results")
        
        # Save configuration
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        logger.info(f"✅ Configuration saved to: {output_path}")
        
        # Save visualization if requested
        if args.visualize:
            vis_path = output_path.parent / f"{output_path.stem}_visualization.png"
            save_visualization(processed_img, detections, str(vis_path), logger)
        
        # Print summary
        print("\n" + "="*60)
        print("✅ PIPELINE COMPLETE")
        print("="*60)
        print(f"Input:  {args.input}")
        print(f"Output: {args.output}")
        print(f"\nExtracted Dimensions:")
        dims = config['dimensions']
        print(f"  Foundation: {dims['foundation_length']}m × {dims['foundation_width']}m")
        print(f"  Stone Section: {dims['stone_section_height']}m")
        print(f"  Wood Section: {dims['wood_section_height']}m")
        print(f"  Windows: {dims['num_wood_windows']} ({dims['wood_window_width']}m × {dims['wood_window_height']}m)")
        print(f"  Door: {dims['door_width']}m × {dims['door_height']}m")
        print(f"  Roof Pitch: {dims['roof_pitch_angle']}°")
        print(f"\nConfidence Score: {config['metadata']['extraction_confidence']:.2f}")
        
        if config['metadata']['validation_warnings']:
            print(f"\n⚠️  Warnings:")
            for warning in config['metadata']['validation_warnings']:
                print(f"  - {warning}")
        
        print("\nNext Steps:")
        print(f"  1. Review and edit: {args.output}")
        print(f"  2. Generate DXF: ./generate_alpine_sennhuette_improved.sh {args.output}")
        print("="*60 + "\n")
        
    except Exception as e:
        logger.error(f"Pipeline failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
