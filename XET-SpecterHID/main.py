import logging
import os
import sys # Though not strictly needed for path if controller handles it, good for general use.

# Attempt to import CoreController.
# The sys.path modification in core/controller.py should make this work if controller.py is imported first,
# or if main.py is run in a way that XET-SpecterHID is implicitly on the path.
# For robustness, especially if main.py is the entry point, ensuring XET-SpecterHID (project root)
# is on sys.path here or before importing core.controller is a good practice.
# However, controller.py already adds PROJECT_ROOT (which is XET-SpecterHID) to sys.path.
# So, when `from core.controller import CoreController` is executed,
# the `core/controller.py` script runs, its sys.path modification occurs,
# and then its own internal imports (like `from obs.obs_connector`) will work.

try:
    from core.controller import CoreController
except ModuleNotFoundError:
    # This fallback is in case core.controller's sys.path append isn't sufficient
    # when main.py is the absolute first entry point.
    # This ensures that the directory containing 'core', 'obs', etc. is on the path.
    # If main.py is in XET-SpecterHID/, then its directory is the project root.
    current_dir = os.path.dirname(os.path.abspath(__file__))
    if current_dir not in sys.path:
        sys.path.insert(0, current_dir) # Add current_dir (XET-SpecterHID) to path
    
    # Try importing again after potentially modifying path
    from core.controller import CoreController


# Configure basic logging
# Using a more specific logger name for messages originating from main.py
logger = logging.getLogger("XET_SpecterHID_Main")
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')

if __name__ == "__main__":
    logger.info("Starting XET-SpecterHID PoC...")

    # Define the path to the configuration file
    # main.py is in XET-SpecterHID/, config/ is a subdirectory
    # CoreController's __main__ block uses a similar logic for its default config path.
    config_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config", "settings.toml")

    controller_instance = None
    try:
        logger.info(f"Loading configuration from: {config_file_path}")
        controller_instance = CoreController(config_path=config_file_path)
        
        logger.info("CoreController initialized. Starting the main loop...")
        controller_instance.run()

    except FileNotFoundError:
        logger.error(f"FATAL: Configuration file not found at {config_file_path}. Cannot start.")
        logger.error("Please ensure 'settings.toml' exists in the 'XET-SpecterHID/config/' directory.")
        logger.error("The CoreController (if run directly) might create a default one, "
                     "but main.py expects it for explicit initialization here.")
    except KeyboardInterrupt:
        logger.info("User requested shutdown (KeyboardInterrupt).")
        if controller_instance:
            logger.info("Attempting to stop CoreController...")
            controller_instance.stop() # Signal the controller to stop its loop
    except ImportError as e:
        logger.error(f"FATAL: Failed to import necessary modules: {e}", exc_info=True)
        logger.error("This might be due to an incorrect project structure or a missing __init__.py in subdirectories if they were treated as packages in a different context.")
        logger.error(f"Current sys.path: {sys.path}")
        # Displaying the project root used by controller.py for diagnostics
        # This requires getting it from controller if possible, or re-calculating
        try:
            from core.controller import PROJECT_ROOT as CONTROLLER_PROJECT_ROOT
            logger.error(f"CoreController's PROJECT_ROOT was: {CONTROLLER_PROJECT_ROOT}")
        except ImportError:
            pass # core.controller might not be importable at this stage
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}", exc_info=True)
        if controller_instance:
            logger.info("Attempting to stop CoreController due to an unexpected error...")
            controller_instance.stop()
    finally:
        # The controller's own finally block in run() will handle OBS disconnection.
        # This is just a final message from main.
        logger.info("XET-SpecterHID PoC terminated.")
```
