"""JSON configuration file generator for CAD system.

Generates valid JSON configuration files compatible with the
QCAD-based floorplan generation system.

Example:
    >>> from cv_modules import ConfigGenerator
    >>> generator = ConfigGenerator()
    >>> config = generator.generate(dimensions, "Alpine Sennhütte")
    >>> generator.save_config(config, "output.json")
"""

import json
from datetime import datetime
from typing import Dict, Any, Optional, Tuple, List
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class ConfigGenerator:
    """Generates JSON configuration files for CAD generation.
    
    Creates properly formatted JSON files compatible with the
    alpine_sennhutte_generator scripts.
    
    Attributes:
        default_scale: Default drawing scale
        default_unit: Default measurement unit
        building_type: Type of building
    """
    
    def __init__(
        self,
        default_scale: str = "1:50",
        default_unit: str = "meters",
        building_type: str = "Alpine Sennhütte"
    ):
        """Initialize the ConfigGenerator.
        
        Args:
            default_scale: Default CAD drawing scale
            default_unit: Default measurement unit
            building_type: Type of building being configured
        """
        self.default_scale = default_scale
        self.default_unit = default_unit
        self.building_type = building_type
        logger.info(f"ConfigGenerator initialized for {building_type}")
    
    def generate(
        self,
        dimensions: Dict[str, Any],
        building_type: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Generate complete JSON configuration.
        
        Args:
            dimensions: Dictionary of building dimensions
            building_type: Override default building type
            metadata: Additional metadata to include
        
        Returns:
            Complete JSON configuration dictionary
        """
        config = {
            "timestamp": datetime.now().isoformat(),
            "building_type": building_type or self.building_type,
            "dimensions": dimensions,
            "scale": self.default_scale,
            "unit": self.default_unit
        }
        
        # Add metadata if provided
        if metadata:
            config["metadata"] = metadata
        
        logger.info(f"Generated config for {config['building_type']}")
        return config
    
    def save_config(
        self,
        config: Dict[str, Any],
        output_path: str,
        indent: int = 2
    ) -> bool:
        """Save configuration to JSON file.
        
        Args:
            config: Configuration dictionary
            output_path: Path to save JSON file
            indent: JSON indentation level
        
        Returns:
            True if successful, False otherwise
        """
        try:
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=indent, ensure_ascii=False)
            
            logger.info(f"Configuration saved to {output_path}")
            return True
        
        except Exception as e:
            logger.error(f"Failed to save configuration: {e}")
            return False
    
    def load_config(self, config_path: str) -> Optional[Dict[str, Any]]:
        """Load configuration from JSON file.
        
        Args:
            config_path: Path to JSON configuration file
        
        Returns:
            Configuration dictionary or None if loading failed
        """
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            logger.info(f"Configuration loaded from {config_path}")
            return config
        
        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
            return None
    
    def validate_config(
        self,
        config: Dict[str, Any]
    ) -> Tuple[bool, List[str]]:
        """Validate configuration structure and required fields.
        
        Args:
            config: Configuration dictionary to validate
        
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        
        # Check required top-level fields
        required_fields = ["timestamp", "building_type", "dimensions", "scale", "unit"]
        for field in required_fields:
            if field not in config:
                errors.append(f"Missing required field: {field}")
        
        # Check required dimension fields
        if "dimensions" in config:
            required_dims = [
                "foundation_length", "foundation_width",
                "stone_section_height", "wood_section_height",
                "door_width", "door_height",
                "wood_window_width", "wood_window_height",
                "roof_pitch_angle"
            ]
            for dim in required_dims:
                if dim not in config["dimensions"]:
                    errors.append(f"Missing required dimension: {dim}")
        
        is_valid = len(errors) == 0
        
        if not is_valid:
            logger.error(f"Config validation failed: {errors}")
        else:
            logger.info("Config validation passed")
        
        return is_valid, errors
    
    def merge_with_defaults(
        self,
        extracted_config: Dict[str, Any],
        default_config_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """Merge extracted config with default values.
        
        Args:
            extracted_config: Configuration from image extraction
            default_config_path: Path to default config file
        
        Returns:
            Merged configuration
        """
        if default_config_path:
            defaults = self.load_config(default_config_path)
            if defaults and "dimensions" in defaults:
                # Merge dimensions, preferring extracted values
                merged_dims = {**defaults["dimensions"], **extracted_config["dimensions"]}
                extracted_config["dimensions"] = merged_dims
                logger.info("Merged with default configuration")
        
        return extracted_config
