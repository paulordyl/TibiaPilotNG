import logging
import base64
from io import BytesIO
from PIL import Image
from obswebsocket import obsws, requests, exceptions

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class OBSConnector:
    """
    Handles connection and frame capture from OBS Studio via WebSocket.
    """
    def __init__(self, host: str, port: int, password: str = None):
        """
        Initializes the OBSConnector.

        Args:
            host (str): The hostname or IP address of the OBS WebSocket server.
            port (int): The port number of the OBS WebSocket server.
            password (str, optional): The password for the OBS WebSocket server. Defaults to None.
        """
        self.host = host
        self.port = port
        self.password = password
        self.ws = None
        self._source_name = None # To be configured if a specific source is needed

    def connect(self) -> bool:
        """
        Establishes the WebSocket connection to OBS.

        Returns:
            bool: True if connection is successful, False otherwise.
        """
        if self.ws and self.ws.ws.connected:
            logger.info("Already connected to OBS.")
            return True

        self.ws = obsws(self.host, self.port, self.password)
        try:
            self.ws.connect()
            logger.info(f"Successfully connected to OBS WebSocket server at {self.host}:{self.port}")
            return True
        except exceptions.ConnectionFailure as e:
            logger.error(f"Failed to connect to OBS WebSocket: {e}")
            self.ws = None # Ensure ws is None if connection failed
            return False
        except BrokenPipeError as e: # Added to catch BrokenPipeError specifically
            logger.error(f"Connection to OBS failed (BrokenPipeError): {e}. Check if OBS is running and WebSocket server is enabled.")
            self.ws = None
            return False
        except ConnectionRefusedError as e: # Added to catch ConnectionRefusedError specifically
            logger.error(f"Connection to OBS refused: {e}. Check if OBS is running and WebSocket server is enabled on {self.host}:{self.port}.")
            self.ws = None
            return False


    def disconnect(self):
        """
        Disconnects from the OBS WebSocket server.
        """
        if self.ws and self.ws.ws.connected:
            try:
                self.ws.disconnect()
                logger.info("Disconnected from OBS WebSocket server.")
            except Exception as e: # Catch any potential error during disconnect
                logger.error(f"Error during disconnection from OBS: {e}")
            finally:
                self.ws = None
        else:
            logger.info("Not connected to OBS, no need to disconnect.")

    def get_source_by_type(self, source_type: str = "monitor_capture", source_name_filter: str = None):
        """
        Attempts to find a source of a specific type (e.g., 'monitor_capture', 'window_capture', 'game_capture').
        Optionally filters by name.
        Returns the name of the first matching source found.
        """
        if not self.ws or not self.ws.ws.connected:
            logger.error("Not connected to OBS. Cannot get sources.")
            return None

        try:
            # GetSourcesList is deprecated, using GetInputList
            inputs_response = self.ws.call(requests.GetInputList())
            inputs = inputs_response.getInputs()

            for item in inputs:
                # The kind of input can be used to identify 'monitor_capture', 'window_capture' etc.
                # However, exact kind names might vary based on OBS version and plugins.
                # Common kinds: 'monitor_capture', 'window_capture', 'game_capture', 'image_source', 'dshow_input' (for webcams)
                # For generic screen capture, 'monitor_capture' (often called 'Display Capture') is common.
                # Or a specific source like 'game_capture' or 'window_capture'.
                # This example prioritizes 'monitor_capture' if no specific filter is given.
                
                # We need to get input settings to check the actual source type for some inputs
                # For now, we rely on the inputKind matching or a user-provided name.
                if source_name_filter and item['inputName'] == source_name_filter:
                    logger.info(f"Found specified source by name: {item['inputName']} of kind {item['inputKind']}")
                    return item['inputName']
                elif not source_name_filter and item['inputKind'] in [source_type, "display_capture", "monitor_capture", "screen_capture_input"]: # Common names for display/monitor capture
                    logger.info(f"Found source of type '{item['inputKind']}': {item['inputName']}")
                    return item['inputName']
            
            if source_name_filter:
                logger.warning(f"Specified source '{source_name_filter}' not found.")
            else:
                logger.warning(f"No source of type '{source_type}' found. Please ensure a screen, window, or game capture source is active in OBS.")
            return None

        except Exception as e:
            logger.error(f"Error getting sources from OBS: {e}")
            return None


    def capture_frame(self, source_name: str = None, output_width: int = None, output_height: int = None) -> Image.Image | None:
        """
        Requests a screenshot from OBS.

        Args:
            source_name (str, optional): The name of the source to capture.
                                         If None, tries to find a 'monitor_capture' or similar.
            output_width (int, optional): Desired width of the output image. OBS will scale.
            output_height (int, optional): Desired height of the output image. OBS will scale.

        Returns:
            PIL.Image.Image | None: The captured image as a Pillow Image object, or None if an error occurs.
        """
        if not self.ws or not self.ws.ws.connected:
            logger.error("Not connected to OBS. Cannot capture frame.")
            return None

        target_source_name = source_name
        if not target_source_name:
            if self._source_name: # Use pre-configured source name if available
                 target_source_name = self._source_name
            else: # Try to auto-detect a suitable source
                target_source_name = self.get_source_by_type("monitor_capture") # Default to monitor capture
                if not target_source_name:
                    target_source_name = self.get_source_by_type("window_capture") # Fallback to window
                if not target_source_name:
                     target_source_name = self.get_source_by_type("game_capture") # Fallback to game
                
                if target_source_name:
                    self._source_name = target_source_name # Cache for next time
                else:
                    logger.error("Could not automatically determine a source to capture. Please specify a source_name.")
                    return None
        
        logger.info(f"Attempting to capture frame from source: {target_source_name}")

        try:
            # GetSourceScreenshot is deprecated, use GetSourceScreenshotRequest
            # OBS API requires sourceName. imageFormat is mandatory.
            # compressionQuality is optional.
            params = {
                'sourceName': target_source_name,
                'imageFormat': 'png', # png is lossless and widely supported
            }
            if output_width:
                params['imageWidth'] = output_width
            if output_height:
                params['imageHeight'] = output_height
            
            response = self.ws.call(requests.GetSourceScreenshot(**params))
            
            if response.ok():
                image_data_b64 = response.getImageData() # Renamed from imageData
                if not image_data_b64:
                    logger.error("Received empty image data from OBS.")
                    return None
                
                # Remove the data URI scheme prefix if present (e.g., "data:image/png;base64,")
                if ',' in image_data_b64:
                    image_data_b64 = image_data_b64.split(',', 1)[1]
                
                img_bytes = base64.b64decode(image_data_b64)
                image = Image.open(BytesIO(img_bytes))
                logger.info(f"Frame captured successfully from '{target_source_name}'. Format: {image.format}, Size: {image.size}")
                return image
            else:
                error_message = response.getError() if hasattr(response, 'getError') else "Unknown error from GetSourceScreenshot"
                status_code = response.getStatus() if hasattr(response, 'getStatus') else "N/A"
                logger.error(f"Failed to capture frame from OBS. Source: '{target_source_name}'. Status: {status_code}, Error: {error_message}")
                # Common errors: Source not found, not a visible source.
                if "Source not found" in str(error_message) or "could not find source" in str(error_message).lower():
                    logger.error(f"Ensure source '{target_source_name}' exists and is correctly spelled in OBS.")
                elif "not interactable" in str(error_message).lower():
                     logger.error(f"Source '{target_source_name}' is not interactable. It might be hidden or part of a non-rendered scene.")
                return None

        except exceptions.ConnectionFailure:
            logger.error("Connection to OBS lost during frame capture.")
            self.ws = None # Mark as disconnected
            return None
        except ConnectionRefusedError: # Catch if OBS was closed or WebSocket server stopped
            logger.error("Connection to OBS refused during frame capture. OBS might have closed or WebSocket server stopped.")
            self.ws = None
            return None
        except Exception as e:
            logger.error(f"An unexpected error occurred during frame capture: {e}")
            # Log the full traceback for debugging if possible
            import traceback
            logger.debug(traceback.format_exc())
            return None

# Example usage for standalone testing (requires config/settings.toml)
if __name__ == "__main__":
    import toml
    import os

    # Determine the correct path to settings.toml relative to this script
    # This script is in XET-SpecterHID/obs/obs_connector.py
    # settings.toml is in XET-SpecterHID/config/settings.toml
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir) # Go up one level from 'obs' to 'XET-SpecterHID'
    config_path = os.path.join(project_root, "config", "settings.toml")

    if not os.path.exists(config_path):
        logger.error(f"Configuration file not found at {config_path}. Cannot run standalone test.")
    else:
        logger.info(f"Loading configuration from: {config_path}")
        try:
            config = toml.load(config_path)
            obs_settings = config.get('obs', {})
            host = obs_settings.get('host', 'localhost')
            port = obs_settings.get('port', 4455)
            password = obs_settings.get('password') # Can be None

            logger.info(f"Attempting to connect to OBS at {host}:{port}")
            
            connector = OBSConnector(host=host, port=port, password=password)
            
            if connector.connect():
                logger.info("Connection successful. Attempting to capture a frame...")
                
                # Attempt to capture (auto-detect source, or specify one)
                # You might need to change "Display Capture" to the actual name of your source in OBS
                # common_source_names = ["Display Capture", "Window Capture", "Game Capture", "Screen Capture"] 
                # frame = None
                # for src_name in common_source_names:
                #     logger.info(f"Trying to capture from source: {src_name}")
                #     frame = connector.capture_frame(source_name=src_name)
                #     if frame:
                #         break
                
                # If specific source names failed, try auto-detection
                # if not frame:
                logger.info("Trying to capture frame with auto-detection...")
                frame = connector.capture_frame() # Auto-detect source

                if frame:
                    try:
                        capture_path = os.path.join(project_root, "obs_capture.png")
                        frame.save(capture_path)
                        logger.info(f"Frame captured and saved to {capture_path}")
                    except Exception as e:
                        logger.error(f"Error saving captured frame: {e}")
                else:
                    logger.warning("Failed to capture frame. Ensure OBS is running, a source is available (e.g., 'Display Capture'), and not hidden.")
                
                connector.disconnect()
            else:
                logger.error("Failed to connect to OBS. Please check OBS settings, ensure WebSocket server is enabled, and credentials in settings.toml are correct.")
                logger.error("OBS WebSocket Server Settings: In OBS, go to Tools -> WebSocket Server Settings. Ensure 'Enable WebSocket server' is checked.")
                logger.error(f"Expected port: {port}, password: {'yes (set)' if password else 'no (not set)'}")

        except FileNotFoundError:
            logger.error(f"Configuration file not found: {config_path}")
        except toml.TomlDecodeError:
            logger.error(f"Error decoding TOML configuration file: {config_path}")
        except KeyError as e:
            logger.error(f"Missing key in configuration file: {e}")
        except Exception as e:
            logger.error(f"An unexpected error occurred during standalone test: {e}")
            import traceback
            logger.debug(traceback.format_exc())
