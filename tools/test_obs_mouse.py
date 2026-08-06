"""Quick test script to simulate Arduino mouse commands via pyautogui.

Usage:
  PYTHONPATH=$(pwd) python3 tools/test_obs_mouse.py

Environment variables:
  ARDUINO_SIMULATE_WITH_PYAUTOGUI=1 (recommended)  -- enable pyautogui fallback
  MOVES  - semicolon-separated commands, e.g. "moveTo,200,200;leftClick,200,200"
  DELAY  - default delay between commands in seconds (default: 0.6)
  DURATION - duration for moveTo (seconds, passed to pyautogui.moveTo) (default: 0.5)
  DRY_RUN - set to 1 to only print commands without executing

This script is configurable so you can test OBS capture and verify mouse actions.
Warning: this will move your system mouse. Save work before running.
"""

import os
import time
import sys

# Ensure simulation fallback is enabled unless explicitly set otherwise
if os.getenv('ARDUINO_SIMULATE_WITH_PYAUTOGUI') is None:
    os.environ['ARDUINO_SIMULATE_WITH_PYAUTOGUI'] = '1'

try:
    from src.utils.ino import sendCommandArduino
except Exception as e:
    print('Failed importing sendCommandArduino:', e)
    sys.exit(1)

# Configuration from environment
MOVES = os.getenv('MOVES')
DELAY = float(os.getenv('DELAY', '0.6'))
DURATION = float(os.getenv('DURATION', '0.5'))
DRY_RUN = os.getenv('DRY_RUN', '0') == '1'

# Default sequence if MOVES not provided
DEFAULT_MOVES = [
    'moveTo,200,200',
    'moveTo,1000,600',
    'leftClick,1000,600',
    'moveTo,1020,620',
    'rightClick,1020,620',
    'scroll,1020,620,-500',
]

# Parse MOVES env into a list
if MOVES:
    seq = [m.strip() for m in MOVES.split(';') if m.strip()]
else:
    seq = DEFAULT_MOVES

# Small helper
def send(cmd, delay=DELAY, duration=DURATION, dry_run=DRY_RUN):
    print('-> Command:', cmd)
    if dry_run:
        print('   (dry-run)')
        return
    # For visibility, print cursor before/after when possible
    try:
        import pyautogui
        try:
            before = pyautogui.position()
            print('   before pos:', before)
        except Exception:
            before = None
    except Exception:
        pyautogui = None
        before = None

    sendCommandArduino(cmd)
    # If using pyautogui-based simulation, wait for move duration
    time.sleep(delay)

    if pyautogui:
        try:
            after = pyautogui.position()
            print('   after pos: ', after)
        except Exception:
            pass


if __name__ == '__main__':
    print('Test OBS mouse script starting. DRY_RUN=', DRY_RUN)
    print('Sequence length:', len(seq))
    for c in seq:
        send(c)
    print('Done. Verify the movement in your OBS preview/recording.')