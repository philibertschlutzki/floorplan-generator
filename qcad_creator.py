import logging
import subprocess
import tempfile
import json
from pathlib import Path
from typing import Dict, Any, List

class QCadCreator:
    """
    Handles the generation of DXF files by interfacing with QCAD.

    This class prepares the configuration data, identifies the best strategy
    to run QCAD (depending on the environment, e.g., headless with xvfb),
    and executes the generation script.
    """

    def __init__(self, logger: logging.Logger = None):
        """
        Initializes the QCadCreator.

        Args:
            logger: Logger instance. If None, a new logger is created.
        """
        self.logger = logger or logging.getLogger(__name__)
        self.js_script = "scripts/alpine_sennhutte_generator_improved.js"

    def _get_qcad_strategies(self, qcad_executable: str) -> List[List[str]]:
        """
        Returns a list of command-line strategies to run QCAD.

        This attempts to handle different environments:
        1.  `xvfb-run`: For headless Linux environments (like Codespaces or CI/CD)
            where a virtual display is needed.
        2.  `flatpak`: For systems where QCAD is installed via Flatpak.
        3.  Direct execution: For standard desktop installations with a GUI.

        Args:
            qcad_executable (str): The name or path of the QCAD executable (default: 'qcad').

        Returns:
            List[List[str]]: A list of command arguments for subprocess calls.
        """
        return [
            ["xvfb-run", "-a", "-s", "-screen 0 1024x768x24 -dpi 96", qcad_executable, "-autostart"],
            ["/usr/bin/flatpak", "run", "org.qcad.qcad", qcad_executable, "-autostart"],
            [qcad_executable, "-platform", "minimal", "-style", "fusion", "-autostart"],
        ]

    def create_dxf(self, config: Dict[str, Any], output_path: str, qcad_executable: str = "qcad") -> bool:
        """
        Generates a DXF file from the given configuration.

        It tries multiple execution strategies until one succeeds or all fail.

        Args:
            config (Dict[str, Any]): The configuration dictionary containing
                dimensions and building parameters.
            output_path (str): The destination path for the generated DXF file.
            qcad_executable (str): The QCAD executable name. Defaults to "qcad".

        Returns:
            bool: True if the DXF file was created successfully, False otherwise.
        """
        self.logger.info(f"Starting DXF generation for {output_path}...")

        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix=".json") as temp_config_file:
            json.dump(config, temp_config_file)
            temp_config_path = temp_config_file.name

        strategies = self._get_qcad_strategies(qcad_executable)
        for i, strategy_args in enumerate(strategies):
            self.logger.info(f"Trying QCAD strategy {i+1}/{len(strategies)}: {strategy_args[0]}")
            try:
                command = strategy_args + [
                    f"--config={temp_config_path}",
                    f"--output={output_path}",
                    self.js_script,
                ]

                process = subprocess.Popen(
                    command,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )

                stdout, stderr = process.communicate(timeout=60)

                if process.returncode == 0 and Path(output_path).exists():
                    self.logger.info("DXF generation successful.")
                    return True
                else:
                    self.logger.warning(f"Strategy failed with return code {process.returncode}")
                    if stdout:
                        self.logger.debug(f"QCAD stdout: {stdout.decode()}")
                    if stderr:
                        self.logger.debug(f"QCAD stderr: {stderr.decode()}")

            except FileNotFoundError:
                self.logger.warning(f"Command '{strategy_args[0]}' not found. Skipping strategy.")
            except subprocess.TimeoutExpired:
                self.logger.warning("QCAD process timed out.")
                process.kill()
            except Exception as e:
                self.logger.error(f"An error occurred while running QCAD: {e}")

        self.logger.error("All QCAD strategies failed. DXF file could not be created.")
        return False
