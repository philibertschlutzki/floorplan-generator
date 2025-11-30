import argparse
import logging
import sys
from pathlib import Path
import json
import cv2
import numpy as np

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
        nargs='+',
        help='Path to the input building image(s). Can be one or more files.'
    )
    parser.add_argument(
        '-o', '--output',
        required=True,
        type=str,
        help='Path to the output DXF file.'
    )
    parser.add_argument(
        '--mode',
        type=str,
        choices=['floorplan', 'facade'],
        default='floorplan',
        help='Mode of operation: "floorplan" (default) or "facade".'
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

    logger.info(f"Starting the interactive generation process in {args.mode} mode.")

    try:
        all_configs = []

        for idx, input_path in enumerate(args.input):
            logger.info(f"Processing image {idx + 1}/{len(args.input)}: {input_path}")

            # Step 1: Image Processing with QA Loop
            logger.info("Step 1/5: Processing the input image...")

            approved = False
            manual_points = None
            processed_img = None
            metadata = None

            while not approved:
                processed_img, metadata = process_image(input_path, manual_points=manual_points, logger=logger)

                # Save preview for user to check
                preview_path = Path(args.output).parent / f"preview_rectified_{idx}.jpg"
                cv2.imwrite(str(preview_path), processed_img)
                print(f"\nPreview of rectification saved to: {preview_path}")
                print("Please check the image.")

                user_response = input("Is the perspective correction correct? (y/n) [y]: ").strip().lower()

                if user_response == 'n':
                    print("\nPlease enter the 4 corner points (x, y) starting from Top-Left, clockwise.")
                    print(f"Original image size (Height x Width): {metadata['original_shape'][0]}x{metadata['original_shape'][1]}")
                    print("Example input: 100, 200")

                    points = []
                    corners = ["Top-Left", "Top-Right", "Bottom-Right", "Bottom-Left"]
                    try:
                        for corner in corners:
                            val = input(f"{corner} (x,y): ")
                            parts = val.replace(',', ' ').split()
                            if len(parts) != 2:
                                raise ValueError
                            x, y = int(parts[0]), int(parts[1])
                            points.append([x, y])

                        manual_points = np.array(points, dtype="float32")
                        logger.info("Recalculating with manual points...")
                    except ValueError:
                        print("Invalid input format. Please try again.")
                        continue
                else:
                    approved = True

            # Step 2: Feature Detection
            logger.info("Step 2/5: Detecting features in the image...")
            detections = detect_features(processed_img, logger=logger)

            if args.visualize:
                # Append index to filename if multiple inputs
                stem = Path(args.output).stem
                suffix = f"_{idx}" if len(args.input) > 1 else ""
                vis_path = Path(args.output).parent / f"{stem}{suffix}_visualization.png"
                save_visualization(processed_img, detections, str(vis_path), logger)

            # Step 3: Interactive Dimension Input
            logger.info("Step 3/5: Gathering dimensions interactively...")
            dimension_provider = InteractiveDimensionProvider(logger=logger)
            # In the future we might pass the mode to get_dimensions if needed
            dimensions_result = dimension_provider.get_dimensions(detections)

            # Step 4: Configuration Generation
            logger.info("Step 4/5: Generating the configuration file...")

            # Add image path to metadata for QCAD to use as background
            dimensions_result['image_path'] = str(input_path)
            dimensions_result['processed_image_path'] = str(Path(args.output).parent / f"processed_{Path(input_path).name}")

            # Save processed image for QCAD reference
            cv2.imwrite(dimensions_result['processed_image_path'], processed_img)

            config = generate_config(dimensions_result, "Alpine Sennhütte", logger=logger)
            all_configs.append(config)

        # Merge configs if we have multiple inputs (e.g. 4 facades)
        # For 'floorplan' mode, we might typically just have one, but let's handle it generally
        final_config = {
            "mode": args.mode,
            "configs": all_configs
        }

        # Save the intermediate JSON config for debugging
        json_output_path = Path(args.output).with_suffix('.json')
        with open(json_output_path, 'w') as f:
            json.dump(final_config, f, indent=2)
        logger.info(f"Intermediate JSON configuration saved to {json_output_path}")

        # Step 5: DXF Creation
        logger.info("Step 5/5: Creating the DXF file...")
        qcad_creator = QCadCreator(logger=logger)

        # Backward compatibility for existing QCAD script if only 1 config and floorplan mode
        if len(all_configs) == 1 and args.mode == 'floorplan':
             success = qcad_creator.create_dxf(all_configs[0], args.output)
        else:
             # Pass the full wrapper config for multi-facade support
             success = qcad_creator.create_dxf(final_config, args.output)

        if success:
            logger.info("Successfully generated the QCAD plan.")
        else:
            logger.error("Failed to generate the QCAD plan.")

    except Exception as e:
        logger.error(f"The process failed: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
