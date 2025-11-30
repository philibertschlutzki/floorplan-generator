#!/usr/bin/env python3
"""
Demonstration Script for Building Plan Generator Capabilities.

This script demonstrates the tool's ability to:
1.  Download images from the internet (simulating a user finding a floorplan or facade).
2.  Process them using the `main.py` workflow in non-interactive mode.
3.  Generate the configuration JSON (and DXF if QCAD is available).
4.  Verify the existence of the output artifacts.
"""

import os
import sys
import requests
import subprocess
import json
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("Demonstration")

# Test Cases
TEST_CASES = [
    {
        "name": "Floorplan Demo",
        "url": "https://upload.wikimedia.org/wikipedia/commons/9/9a/Sample_Floorplan.jpg",
        "mode": "floorplan",
        "output_dir": "output/demo_floorplan",
        "output_filename": "demo_floorplan.dxf"
    },
    {
        "name": "Facade Demo",
        # Reuse the floorplan image to ensure test stability, but process in 'facade' mode
        # to demonstrate the pipeline handles the mode switch correctly.
        "url": "https://upload.wikimedia.org/wikipedia/commons/9/9a/Sample_Floorplan.jpg",
        "mode": "facade",
        "output_dir": "output/demo_facade",
        "output_filename": "demo_facade.dxf"
    }
]

def download_image(url: str, save_path: Path) -> bool:
    """Downloads an image from a URL to the specified path."""
    try:
        logger.info(f"Downloading {url}...")
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, stream=True, timeout=10)
        response.raise_for_status()
        with open(save_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        logger.info(f"Saved to {save_path}")
        return True
    except Exception as e:
        logger.error(f"Failed to download image: {e}")
        return False

def run_pipeline(input_path: Path, output_path: Path, mode: str) -> bool:
    """Runs the main.py pipeline in non-interactive mode."""
    command = [
        sys.executable, "main.py",
        "--input", str(input_path),
        "--output", str(output_path),
        "--mode", mode,
        "--non-interactive",
        "--visualize"
    ]

    logger.info(f"Running pipeline: {' '.join(command)}")
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            logger.error(f"Pipeline failed with return code {result.returncode}")
            logger.error(f"STDERR: {result.stderr}")
            logger.error(f"STDOUT: {result.stdout}")
            return False

        logger.info("Pipeline executed successfully.")
        return True
    except Exception as e:
        logger.error(f"Failed to run pipeline: {e}")
        return False

def verify_artifacts(output_path: Path) -> bool:
    """Verifies that the expected output files exist."""
    success = True

    # 1. Check for JSON config
    json_path = output_path.with_suffix('.json')
    if json_path.exists():
        logger.info(f"✅ JSON Config found: {json_path}")
        # Validate valid JSON
        try:
            with open(json_path, 'r') as f:
                json.load(f)
            logger.info("   JSON content is valid.")
        except json.JSONDecodeError:
            logger.error("   JSON content is invalid!")
            success = False
    else:
        logger.error(f"❌ JSON Config missing: {json_path}")
        success = False

    # 2. Check for Processed Image (Preview/Reference)
    # The tool saves "processed_<filename>" in the output directory's parent
    # The output path is usually like "output/demo/file.dxf"
    # The code says: Path(args.output).parent / f"processed_{Path(input_path).name}"
    # Wait, in the main.py:
    # processed_image_path = str(Path(args.output).parent / f"processed_{Path(input_path).name}")
    # But we need to know the input filename to check this.
    # Let's just check the visualization if enabled.

    # 3. Check for Visualization
    vis_path = output_path.parent / f"{output_path.stem}_visualization.png"
    if vis_path.exists():
         logger.info(f"✅ Visualization found: {vis_path}")
    else:
         logger.warning(f"⚠️ Visualization missing: {vis_path} (Maybe visualization failed or was skipped?)")

    # 4. Check for DXF (might fail if QCAD is missing, so we just log it)
    if output_path.exists():
        logger.info(f"✅ DXF file found: {output_path}")
    else:
        logger.warning(f"⚠️ DXF file missing: {output_path} (Expected if QCAD is not installed)")

    return success

def main():
    logger.info("Starting Demonstration...")

    overall_success = True

    for case in TEST_CASES:
        logger.info(f"\n--- Running Case: {case['name']} ---")

        # Setup paths
        out_dir = Path(case['output_dir'])
        out_dir.mkdir(parents=True, exist_ok=True)

        input_filename = "input_image.jpg"
        input_path = out_dir / input_filename
        output_path = out_dir / case['output_filename']

        # 1. Download
        if not download_image(case['url'], input_path):
            logger.error(f"Skipping case {case['name']} due to download failure.")
            overall_success = False
            continue

        # 2. Run Pipeline
        if not run_pipeline(input_path, output_path, case['mode']):
            logger.error(f"Case {case['name']} pipeline failed.")
            overall_success = False
            continue

        # 3. Verify
        if not verify_artifacts(output_path):
            logger.error(f"Case {case['name']} verification failed.")
            overall_success = False
        else:
            logger.info(f"Case {case['name']} passed validation.")

    if overall_success:
        logger.info("\n🎉 All demonstration cases completed successfully!")
        sys.exit(0)
    else:
        logger.error("\nSome cases failed.")
        sys.exit(1)

if __name__ == "__main__":
    main()
