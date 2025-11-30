import logging
from typing import Dict, Any

class InteractiveDimensionProvider:
    """
    Manages the interactive session with the user to gather real-world dimensions.

    This class presents the user with detected features and default values, allowing
    them to override or confirm the dimensions. This step is crucial for accurate
    scaling of the generated CAD plan.
    """

    def __init__(self, logger: logging.Logger = None, defaults: Dict[str, Any] = None):
        """
        Initializes the InteractiveDimensionProvider.

        Args:
            logger: Logger instance.
            defaults: A dictionary of default values to use if the user skips input.
        """
        self.logger = logger or logging.getLogger(__name__)
        self.defaults = defaults or self._get_default_values()

    def _get_default_values(self) -> Dict[str, float]:
        """
        Returns a dictionary of standard default values for an 'Alpenhütte'.

        Returns:
            Dict[str, float]: Default dimensions in meters.
        """
        return {
            'foundation_length': 8.5,
            'foundation_width': 7.0,
            'stone_section_height': 1.8,
            'stone_wall_thickness': 0.5,
            'door_width': 1.0,
            'door_height': 2.0,
            'door_distance_from_edge': 1.2,
            'wood_section_height': 2.5,
            'log_diameter': 0.2,
            'wood_window_width': 1.2,
            'wood_window_height': 1.0,
            'roof_pitch_angle': 35.0,
            'roof_overhang': 0.5,
        }

    def _prompt_for_float(self, prompt_text: str, default: float) -> float:
        """
        Helper method to prompt the user for a floating-point value.

        Args:
            prompt_text (str): The question to ask the user.
            default (float): The fallback value if the user enters nothing.

        Returns:
            float: The user's input or the default value.
        """
        while True:
            try:
                user_input = input(f"{prompt_text} (default: {default}): ").strip()
                if not user_input:
                    return default
                return float(user_input)
            except ValueError:
                self.logger.warning("Invalid input. Please enter a number.")

    def get_dimensions(self, detections: Dict[str, Any]) -> Dict[str, Any]:
        """
        Conducts the interactive session to gather all necessary dimensions.

        It adapts the questions based on what was detected (e.g., if no windows
        were detected, it might ask about them anyway or skip detailed window questions
        depending on logic).

        Args:
            detections (Dict[str, Any]): The output from the FeatureDetector.

        Returns:
            Dict[str, Any]: A comprehensive dictionary of dimensions ready for configuration.
                Includes metadata like 'confidence' and 'validation'.
        """
        self.logger.info("Starting interactive dimension input...")
        dimensions = {}

        print("\nPlease provide the dimensions for the detected features.")
        print("Press Enter to accept the default value shown in parentheses.")

        # Foundation
        dimensions['foundation_length'] = self._prompt_for_float(
            "Enter foundation length (in meters)", self.defaults['foundation_length']
        )
        dimensions['foundation_width'] = self._prompt_for_float(
            "Enter foundation width (in meters)", self.defaults['foundation_width']
        )

        # Stone Section
        dimensions['stone_section_height'] = self._prompt_for_float(
            "Enter stone section height (in meters)", self.defaults['stone_section_height']
        )
        dimensions['stone_wall_thickness'] = self._prompt_for_float(
            "Enter stone wall thickness (in meters)", self.defaults['stone_wall_thickness']
        )

        # Door
        if detections.get('doors'):
            dimensions['door_width'] = self._prompt_for_float(
                "Enter door width (in meters)", self.defaults['door_width']
            )
            dimensions['door_height'] = self._prompt_for_float(
                "Enter door height (in meters)", self.defaults['door_height']
            )
            dimensions['door_distance_from_edge'] = self._prompt_for_float(
                "Enter door distance from edge (in meters)", self.defaults['door_distance_from_edge']
            )

        # Wood Section
        dimensions['wood_section_height'] = self._prompt_for_float(
            "Enter wood section height (in meters)", self.defaults['wood_section_height']
        )
        dimensions['log_diameter'] = self._prompt_for_float(
            "Enter log diameter (in meters)", self.defaults['log_diameter']
        )

        # Windows
        if detections.get('windows'):
            num_windows = len(detections['windows'])
            dimensions['num_wood_windows'] = num_windows
            print(f"\nDetected {num_windows} window(s).")

            dimensions['wood_window_width'] = self._prompt_for_float(
                "Enter width for windows (in meters)", self.defaults['wood_window_width']
            )
            dimensions['wood_window_height'] = self._prompt_for_float(
                "Enter height for windows (in meters)", self.defaults['wood_window_height']
            )

        # Roof
        if detections.get('roof'):
            dimensions['roof_pitch_angle'] = self._prompt_for_float(
                "Enter roof pitch angle (in degrees)", self.defaults['roof_pitch_angle']
            )
            dimensions['roof_overhang'] = self._prompt_for_float(
                "Enter roof overhang (in meters)", self.defaults['roof_overhang']
            )

        self.logger.info("Interactive dimension input complete.")

        return {
            'dimensions': dimensions,
            'confidence': 1.0,  # Manual input is considered high confidence
            'validation': {'warnings': []},
            'scale_used': 'manual_input'
        }
