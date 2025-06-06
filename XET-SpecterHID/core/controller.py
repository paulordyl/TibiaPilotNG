import logging
import time
import toml
import os
import sys

# Adjust Python path to include parent directory (XET-SpecterHID)
# This allows imports like from obs.obs_connector
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
sys.path.append(PROJECT_ROOT)

try:
    from obs.obs_connector import OBSConnector
    from vision.screen_parser import ScreenParser
    from input.emulator import InputEmulator
except ModuleNotFoundError as e:
    # This block helps in diagnosing path issues if the sys.path.append doesn't work as expected
    # or if there's a typo in module/class names.
    print(f"Failed to import modules. Current sys.path: {sys.path}")
    print(f"PROJECT_ROOT: {PROJECT_ROOT}")
    # List contents of PROJECT_ROOT to help debug
    print(f"Contents of PROJECT_ROOT ({PROJECT_ROOT}): {os.listdir(PROJECT_ROOT)}")
    if os.path.exists(os.path.join(PROJECT_ROOT, "obs")):
        print(f"Contents of obs/ ({os.path.join(PROJECT_ROOT, 'obs')}): {os.listdir(os.path.join(PROJECT_ROOT, 'obs'))}")
    if os.path.exists(os.path.join(PROJECT_ROOT, "vision")):
        print(f"Contents of vision/ ({os.path.join(PROJECT_ROOT, 'vision')}): {os.listdir(os.path.join(PROJECT_ROOT, 'vision'))}")
    if os.path.exists(os.path.join(PROJECT_ROOT, "input")):
        print(f"Contents of input/ ({os.path.join(PROJECT_ROOT, 'input')}): {os.listdir(os.path.join(PROJECT_ROOT, 'input'))}")
    raise

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class CoreController:
    """
    Orchestrates screen capture, visual analysis, and input emulation.
    """
    def __init__(self, config_path: str):
        """
        Initializes the CoreController.

        Args:
            config_path (str): Path to the TOML configuration file.
        """
        logger.info(f"Initializing CoreController with config: {config_path}")
        try:
            self.config = toml.load(config_path)
        except FileNotFoundError:
            logger.error(f"Configuration file not found at: {config_path}")
            raise
        except toml.TomlDecodeError as e:
            logger.error(f"Error decoding TOML configuration file {config_path}: {e}")
            raise

        # OBS Connector settings
        obs_config = self.config.get('obs', {})
        self.obs_connector = OBSConnector(
            host=obs_config.get('host', 'localhost'),
            port=obs_config.get('port', 4455),
            password=obs_config.get('password')
        )

        # Screen Parser settings
        vision_config = self.config.get('vision', {})
        self.screen_parser = ScreenParser(
            roi_x=vision_config.get('roi_x', 0),
            roi_y=vision_config.get('roi_y', 0),
            roi_width=vision_config.get('roi_width', -1),
            roi_height=vision_config.get('roi_height', -1),
            target_color_hsv_lower=tuple(vision_config.get('target_hsv_lower', [35, 100, 100])),
            target_color_hsv_upper=tuple(vision_config.get('target_hsv_upper', [85, 255, 255])),
            detection_threshold_pixels=vision_config.get('detection_threshold_pixels', 1000)
        )

        # Input Emulator settings
        emulator_config = self.config.get('input_emulator', {})
        self.input_emulator = InputEmulator(
            min_delay_ms=emulator_config.get('min_delay_ms', 50),
            max_delay_ms=emulator_config.get('max_delay_ms', 150)
        )
        self.action_on_detection = emulator_config.get('action_on_detection', 'press_space')


        # Capture settings
        capture_config = self.config.get('capture', {})
        self.capture_delay_ms = capture_config.get('delay_ms', 250)
        self.capture_source_name = obs_config.get('source_name', None) # Optional: specify source in config
        self.capture_width = obs_config.get('capture_width', None) # Optional: specify capture width
        self.capture_height = obs_config.get('capture_height', None) # Optional: specify capture height


        self.running = False
        logger.info("CoreController initialized successfully.")

    def run(self):
        """
        Starts the main control loop: capture -> analyze -> act.
        """
        self.running = True
        logger.info("CoreController run loop started.")

        if not self.obs_connector.connect():
            logger.error("Failed to connect to OBS. Exiting run loop.")
            self.running = False
            return

        try:
            while self.running:
                loop_start_time = time.time()

                # 1. Capture frame
                logger.debug(f"Attempting frame capture from source: {self.capture_source_name or 'auto-detect'}")
                frame = self.obs_connector.capture_frame(
                    source_name=self.capture_source_name,
                    output_width=self.capture_width,
                    output_height=self.capture_height
                )

                if frame:
                    # 2. Analyze frame
                    logger.debug("Frame captured, starting analysis.")
                    analysis_result = self.screen_parser.analyze_frame(frame)
                    logger.info(f"Frame analysis result: {analysis_result}")

                    # 3. Decision Logic & Action
                    if analysis_result.get("status") == "target_color_detected":
                        logger.info(f"Target detected. Executing action: {self.action_on_detection}")
                        self.input_emulator.execute_action(self.action_on_detection)
                    else:
                        logger.info("Target not detected or other status. No action taken.")
                else:
                    logger.warning("Frame capture failed. Skipping analysis and action for this iteration.")
                    # Consider adding logic here for reconnection attempts if obs connection seems lost
                    if not self.obs_connector.ws or not self.obs_connector.ws.ws.connected:
                        logger.error("OBS connection lost. Attempting to reconnect...")
                        if self.obs_connector.connect():
                            logger.info("Successfully reconnected to OBS.")
                        else:
                            logger.error("Failed to reconnect to OBS. Will retry next cycle or exit.")
                            time.sleep(5) # Wait before trying again or exiting

                # 4. Wait for the next cycle
                loop_end_time = time.time()
                processing_time_ms = (loop_end_time - loop_start_time) * 1000
                wait_time_s = max(0, (self.capture_delay_ms - processing_time_ms) / 1000)

                if wait_time_s > 0:
                    logger.debug(f"Processing took {processing_time_ms:.2f}ms. Waiting for {wait_time_s:.2f}s.")
                    time.sleep(wait_time_s)
                else:
                    logger.warning(f"Processing time ({processing_time_ms:.2f}ms) exceeded capture delay ({self.capture_delay_ms}ms). Running next cycle immediately.")

        except KeyboardInterrupt:
            logger.info("KeyboardInterrupt received. Stopping CoreController.")
            self.running = False
        except Exception as e:
            logger.error(f"An unexpected error occurred in the run loop: {e}", exc_info=True)
            self.running = False
        finally:
            logger.info("Exiting run loop. Disconnecting from OBS.")
            self.obs_connector.disconnect()
            logger.info("CoreController stopped.")

    def stop(self):
        """
        Signals the controller to stop its run loop.
        """
        logger.info("Stop signal received for CoreController.")
        self.running = False


if __name__ == "__main__":
    logger.info("Starting CoreController in standalone mode...")

    # Construct the path to settings.toml relative to this script
    # core/controller.py -> config/settings.toml
    # SCRIPT_DIR is XET-SpecterHID/core
    # PROJECT_ROOT is XET-SpecterHID
    default_config_path = os.path.join(PROJECT_ROOT, "config", "settings.toml")

    if not os.path.exists(default_config_path):
        logger.error(f"CRITICAL: Default configuration file not found at {default_config_path}")
        logger.error("Please ensure 'settings.toml' exists in the 'XET-SpecterHID/config/' directory.")
        # Create a dummy settings.toml if it's missing for basic testing,
        # but this won't have proper OBS credentials.
        logger.warning("Attempting to create a minimal settings.toml for testing purposes.")
        try:
            os.makedirs(os.path.dirname(default_config_path), exist_ok=True)
            with open(default_config_path, "w") as f:
                f.write("[obs]\n")
                f.write('host = "localhost"\n')
                f.write("port = 4455\n")
                f.write("# password = \"your_obs_password\"\n\n")
                f.write("[capture]\n")
                f.write("delay_ms = 500\n\n")
                f.write("[vision]\n")
                f.write("target_hsv_lower = [35, 100, 100]\n")
                f.write("target_hsv_upper = [85, 255, 255]\n")
                f.write("detection_threshold_pixels = 100\n\n")
                f.write("[input_emulator]\n")
                f.write("min_delay_ms = 50\n")
                f.write("max_delay_ms = 150\n")
                f.write('action_on_detection = "press_space"\n')
            logger.info(f"Minimal settings.toml created at {default_config_path}. Please review and configure OBS settings.")
        except Exception as e:
            logger.error(f"Could not create minimal settings.toml: {e}")
            sys.exit(1) # Exit if config cannot be found or created

    try:
        controller = CoreController(config_path=default_config_path)
        controller.run()
    except FileNotFoundError:
        logger.error(f"Failed to initialize CoreController due to missing config file. Ensure {default_config_path} exists.")
    except toml.TomlDecodeError:
        logger.error(f"Failed to initialize CoreController due to TOML decoding error in {default_config_path}.")
    except Exception as e:
        logger.error(f"An unexpected error occurred during CoreController standalone execution: {e}", exc_info=True)

```
