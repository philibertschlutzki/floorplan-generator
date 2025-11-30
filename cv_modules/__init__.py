"""Computer Vision modules for building feature extraction from images.

This package provides functionality to:
- Preprocess building images (perspective correction, denoising)
- Detect architectural features (walls, windows, doors, roof)
- Extract dimensional information
- Generate JSON configuration files for CAD generation

Modules:
    image_preprocessor: Image preprocessing and enhancement
    feature_detector: Building feature detection using OpenCV
    dimension_extractor: Dimensional analysis and measurements
    config_generator: JSON configuration file generation
"""

__version__ = "3.0.0"
__author__ = "Philibert Schlutzki"

from .image_preprocessor import ImagePreprocessor
from .feature_detector import FeatureDetector
from .dimension_extractor import DimensionExtractor
from .config_generator import ConfigGenerator
from .interactive_scaler import InteractiveScaler

__all__ = [
    "ImagePreprocessor",
    "FeatureDetector",
    "DimensionExtractor",
    "ConfigGenerator",
    "InteractiveScaler",
]
