"""Quick test script to simulate Arduino mouse commands via pyautogui.

Usage:
  python tools/test_obs_mouse.py

Set ARDUINO_SIMULATE_WITH_PYAUTOGUI=1 so the project's sendCommandArduino will use
pyautogui to simulate the mouse movements when no Arduino is connected.

This script sends a few move/click commands with small delays so you can watch
OBS capture and verify the cursor movement/clicks.

Warning: this will move your system mouse. Close apps or save work if needed.
"""

import os
import time

# Ensure simulation fallback is enabled
os.environ['ARDUINO_SIMULATE_WITH_PYAUTOGUI'] = '1'

from src.utils.ino import sendCommandArduino

# Small helper
def send(cmd, delay=0.6):
    print('Sending:', cmd)
    sendCommandArduino(cmd)
    time.sleep(delay)

if __name__ == '__main__':
    # Move to top-left-ish
    send('moveTo,200,200', 1.0)
    # Move to center-ish
    send('moveTo,800,450', 1.0)
    # Left click at center
    send('leftClick,800,450', 0.5)
    # Move slightly and right click
    send('moveTo,820,470', 0.6)
    send('rightClick,820,470', 0.5)
    # Scroll down
    send('scroll,820,470,-500', 0.6)
    print('Done. Verify the movement in your OBS preview/recording.')