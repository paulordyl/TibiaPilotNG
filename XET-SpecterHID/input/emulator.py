import logging
import time
import random
import pyautogui

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class InputEmulator:
    """
    Simulates user input (e.g., key presses) with human-like random delays.
    """
    def __init__(self, min_delay_ms: int = 50, max_delay_ms: int = 150):
        """
        Initializes the InputEmulator.

        Args:
            min_delay_ms (int): Minimum delay in milliseconds before simulating input.
            max_delay_ms (int): Maximum delay in milliseconds before simulating input.
        """
        if min_delay_ms < 0 or max_delay_ms < 0:
            raise ValueError("Delay values cannot be negative.")
        if min_delay_ms > max_delay_ms:
            raise ValueError("min_delay_ms cannot be greater than max_delay_ms.")
            
        self.min_delay_ms = min_delay_ms
        self.max_delay_ms = max_delay_ms
        logger.info(f"InputEmulator initialized with delays: min={min_delay_ms}ms, max={max_delay_ms}ms.")

        # Mapping of action commands to pyautogui key names
        # This can be expanded as needed.
        self.action_to_key_map = {
            "press_space": "space",
            "press_enter": "enter",
            "press_esc": "escape",
            "press_up": "up",
            "press_down": "down",
            "press_left": "left",
            "press_right": "right",
            "press_a": "a",
            "press_w": "w",
            "press_s": "s",
            "press_d": "d",
            # Add more actions and corresponding keys here
            # e.g., "press_ctrl_c": ("ctrl", "c") - pyautogui handles tuples for hotkeys
        }

    def _apply_delay(self):
        """
        Applies a random delay between min_delay_ms and max_delay_ms.
        """
        if self.min_delay_ms == self.max_delay_ms == 0: # No delay if both are zero
            return 0
            
        delay_ms = random.uniform(self.min_delay_ms, self.max_delay_ms)
        delay_s = delay_ms / 1000.0
        logger.debug(f"Applying delay of {delay_ms:.2f}ms.")
        time.sleep(delay_s)
        return delay_ms

    def execute_action(self, action_command: str):
        """
        Executes a predefined action, like pressing a key.

        Args:
            action_command (str): The command representing the action to perform
                                  (e.g., "press_space").
        """
        if action_command not in self.action_to_key_map:
            logger.error(f"Unknown action command: '{action_command}'. No action performed.")
            return

        key_to_press = self.action_to_key_map[action_command]
        
        applied_delay_ms = self._apply_delay()
        
        try:
            pyautogui.press(key_to_press)
            logger.info(f"Executed action: '{action_command}' (pressed key: '{key_to_press}') after {applied_delay_ms:.2f}ms delay.")
        except Exception as e:
            # pyautogui can raise various exceptions, e.g., if it fails to control the mouse/keyboard
            # (often due to permissions or specific OS environments like headless servers)
            logger.error(f"Error during pyautogui.press('{key_to_press}') for action '{action_command}': {e}", exc_info=True)
            logger.error("Ensure your environment allows pyautogui to control input. "
                         "On some systems, you might need to grant accessibility permissions. "
                         "Avoid running in headless environments if not configured for virtual displays.")


# Example usage for standalone testing
if __name__ == "__main__":
    # Note: PyAutoGUI can affect your computer. Be ready to interrupt if necessary
    # (e.g., by moving the mouse to a corner quickly if pyautogui.FAILSAFE is True, default).
    
    # Test with default delays
    emulator = InputEmulator() # Default: 50-150ms

    logger.info("Starting standalone test for InputEmulator...")
    logger.info("IMPORTANT: PyAutoGUI will attempt to control your keyboard.")
    logger.info("Test will simulate pressing SPACE, then ENTER, then an INVALID action.")
    logger.info("You have 5 seconds to switch to a text editor or safe input field...")
    time.sleep(5)

    logger.info("Simulating 'press_space'...")
    emulator.execute_action("press_space")
    logger.info("Spacebar should have been pressed.")
    
    time.sleep(1) # Pause between actions for clarity

    logger.info("Simulating 'press_enter'...")
    emulator.execute_action("press_enter")
    logger.info("Enter key should have been pressed.")

    time.sleep(1)

    logger.info("Attempting an unknown action 'do_a_barrel_roll'...")
    emulator.execute_action("do_a_barrel_roll") # Should be handled gracefully
    logger.info("Unknown action should have been logged as an error.")

    logger.info("--- Testing with zero delay ---")
    zero_delay_emulator = InputEmulator(min_delay_ms=0, max_delay_ms=0)
    logger.info("Simulating 'press_a' with zero delay (focus a text field!)...")
    time.sleep(3)
    zero_delay_emulator.execute_action("press_a")
    logger.info("'a' key should have been pressed instantly.")
    
    logger.info("--- Testing custom delays (e.g., longer delays) ---")
    long_delay_emulator = InputEmulator(min_delay_ms=1000, max_delay_ms=2000) # 1-2 seconds
    logger.info("Simulating 'press_w' with 1-2 second delay (focus a text field!)...")
    time.sleep(3)
    long_delay_emulator.execute_action("press_w")
    logger.info("'w' key should have been pressed after 1-2 seconds.")

    try:
        logger.info("--- Testing invalid delay initialization ---")
        InputEmulator(min_delay_ms=-10, max_delay_ms=10)
    except ValueError as e:
        logger.info(f"Caught expected error for invalid delays: {e}")

    try:
        logger.info("--- Testing min_delay > max_delay initialization ---")
        InputEmulator(min_delay_ms=100, max_delay_ms=10)
    except ValueError as e:
        logger.info(f"Caught expected error for min_delay > max_delay: {e}")


    logger.info("InputEmulator standalone test completed.")
    logger.info("Check your active text input field for ' space', 'enter', 'a', 'w'.")

```
