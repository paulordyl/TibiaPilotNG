"""Capture a screenshot using the project's getScreenshot (dxcam) or fallback to pyautogui.

Saves a grayscale PNG to tools/latest_screenshot.png for use with the locate tester.
"""

import os
import sys

OUT = os.path.join(os.path.dirname(__file__), 'latest_screenshot.png')


def main():
    # Try to use project getScreenshot which returns grayscale image (numpy array)
    try:
        PY_PATH = os.getcwd()
        if PY_PATH not in sys.path:
            sys.path.insert(0, PY_PATH)
        from src.utils.core import getScreenshot
        import cv2
        img = getScreenshot()
        if img is None:
            print('getScreenshot returned None — trying pyautogui fallback')
            raise RuntimeError('no screenshot')
        # img should be grayscale (2D)
        cv2.imwrite(OUT, img)
        print('Saved screenshot to', OUT)
        return
    except Exception as e:
        print('Project getScreenshot failed:', e)

    # Fallback to pyautogui
    try:
        import pyautogui
        import numpy as np
        import cv2
        img_rgb = pyautogui.screenshot()
        arr = cv2.cvtColor(np.array(img_rgb), cv2.COLOR_RGB2GRAY)
        cv2.imwrite(OUT, arr)
        print('Saved fallback screenshot to', OUT)
    except Exception as e:
        print('Failed to capture screenshot with pyautogui:', e)
        sys.exit(1)


if __name__ == '__main__':
    main()
