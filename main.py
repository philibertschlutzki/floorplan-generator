import argparse
import logging
import sys
from pathlib import Path
import json

from generate_from_image import process_image, detect_features, generate_config, save_visualization
from interactive_dimension_provider import InteractiveDimensionProvider
from qcad_creator import QCadCreator

def setup_logging(debug: bool = False) -> logging.Logger:
    """Configure logging based on the debug flag."""
    level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('logs/main_workflow.log', mode='a')
        ]
    )
    return logging.getLogger(__name__)

def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='Generate a QCAD plan from a building image with interactive dimension input.'
    )
    parser.add_argument(
        '-i', '--input',
        required=True,
        type=str,
        help='Path to the input building image.'
    )
    parser.add_argument(
        '-o', '--output',
        required=True,
        type=str,
        help='Path to the output DXF file.'
    )
    parser.add_argument(
        '--visualize',
        action='store_true',
        help='Save a visualization of the detected features.'
    )
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug logging.'
    )
    return parser.parse_args()

def main():
    """Main execution function."""
    args = parse_arguments()

    Path('logs').mkdir(exist_ok=True)
    logger = setup_logging(args.debug)

    logger.info("Starting the interactive floorplan generation process.")

    try:
        # Step 1: Image Processing
        logger.info("Step 1/5: Processing the input image...")
        processed_img, _ = process_image(args.input, logger=logger)

        # Step 2: Feature Detection
        logger.info("Step 2/5: Detecting features in the image...")
        detections = detect_features(processed_img, logger=logger)

        if args.visualize:
            vis_path = Path(args.output).parent / f"{Path(args.output).stem}_visualization.png"
            save_visualization(processed_img, detections, str(vis_path), logger)

        # Step 3: Interactive Dimension Input
        logger.info("Step 3/5: Gathering dimensions interactively...")
        dimension_provider = InteractiveDimensionProvider(logger=logger)
        dimensions_result = dimension_provider.get_dimensions(detections)

        # Step 4: Configuration Generation
        logger.info("Step 4/5: Generating the configuration file...")
        config = generate_config(dimensions_result, "Alpine Sennhütte", logger=logger)

        # Save the intermediate JSON config for debugging
        json_output_path = Path(args.output).with_suffix('.json')
        with open(json_output_path, 'w') as f:
            json.dump(config, f, indent=2)
        logger.info(f"Intermediate JSON configuration saved to {json_output_path}")

        # Step 5: DXF Creation
        logger.info("Step 5/5: Creating the DXF file...")
        qcad_creator = QCadCreator(logger=logger)
        success = qcad_creator.create_dxf(config, args.output)

        if success:
            logger.info("Successfully generated the QCAD plan.")
        else:
            logger.error("Failed to generate the QCAD plan.")

    except Exception as e:
        logger.error(f"The process failed: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
