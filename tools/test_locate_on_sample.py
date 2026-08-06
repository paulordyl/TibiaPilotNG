"""Test src.utils.core.locate against a captured screenshot.

Usage:
  PYTHONPATH=$(pwd) python3 tools/test_locate_on_sample.py [x y w h]
  or
  PYTHONPATH=$(pwd) TEMPLATE_RECT="x,y,w,h" python3 tools/test_locate_on_sample.py

This script will:
 - ensure tools/latest_screenshot.png exists (call capture_screenshot if needed)
 - crop the template region and save as tools/template.png
 - call src.utils.core.locate and locateMultiple and print results
 - save tools/matches.png with rectangles drawn around found matches
"""

import os
import sys
import cv2
import numpy as np

TOOLS_DIR = os.path.dirname(__file__)
SSHOT = os.path.join(TOOLS_DIR, 'latest_screenshot.png')
TEMPLATE_OUT = os.path.join(TOOLS_DIR, 'template.png')
MATCH_OUT = os.path.join(TOOLS_DIR, 'matches.png')


def ensure_screenshot():
    if os.path.exists(SSHOT):
        print('Found existing screenshot:', SSHOT)
        return
    print('No screenshot found, capturing one now...')
    cmd = f'PYTHONPATH=$(pwd) python3 {os.path.join(TOOLS_DIR, "capture_screenshot.py")}'
    rc = os.system(cmd)
    if rc != 0 or not os.path.exists(SSHOT):
        print('Failed to capture screenshot; aborting')
        sys.exit(1)


def parse_rect_from_args():
    # Priority: CLI args, then TEMPLATE_RECT env var
    if len(sys.argv) >= 5:
        try:
            x = int(sys.argv[1]); y = int(sys.argv[2]); w = int(sys.argv[3]); h = int(sys.argv[4])
            return x, y, w, h
        except Exception:
            pass
    tr = os.getenv('TEMPLATE_RECT')
    if tr:
        try:
            parts = [int(p) for p in tr.split(',')]
            if len(parts) == 4:
                return parts[0], parts[1], parts[2], parts[3]
        except Exception:
            pass
    return None


def load_image(path):
    img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        print('Failed to read image:', path)
        sys.exit(1)
    return img


if __name__ == '__main__':
    ensure_screenshot()
    rect = parse_rect_from_args()
    if rect is None:
        print('No template rectangle provided. Provide x y w h as args or TEMPLATE_RECT env var.')
        print('Example: PYTHONPATH=$(pwd) TEMPLATE_RECT="100,200,30,30" python3 tools/test_locate_on_sample.py')
        sys.exit(1)

    x, y, w, h = rect
    print(f'Using template rect x={x}, y={y}, w={w}, h={h}')

    screenshot = load_image(SSHOT)
    # guard bounds
    h_img, w_img = screenshot.shape
    if x < 0 or y < 0 or x + w > w_img or y + h > h_img:
        print('Template rect out of bounds for screenshot size', (w_img, h_img))
        sys.exit(1)

    template = screenshot[y:y+h, x:x+w]
    cv2.imwrite(TEMPLATE_OUT, template)
    print('Saved template to', TEMPLATE_OUT)

    # Import locate functions from project
    PY_PATH = os.getcwd()
    if PY_PATH not in sys.path:
        sys.path.insert(0, PY_PATH)
    try:
        from src.utils.core import locate, locateMultiple
    except Exception as e:
        print('Failed to import locate from project:', e)
        sys.exit(1)

    print('Running locate (single-match)')
    try:
        res = locate(screenshot, template, confidence=0.7)
    except Exception as e:
        print('locate threw exception:', e)
        res = None
    print('locate result:', res)

    print('\nRunning locateMultiple (all matches >= confidence)')
    try:
        multi = locateMultiple(screenshot, template, confidence=0.7)
    except Exception as e:
        print('locateMultiple threw exception:', e)
        multi = []
    print('Found matches count:', len(multi))
    for m in multi[:20]:
        print('  match:', m)

    # Draw rectangles on a color copy to visualize
    color = cv2.cvtColor(screenshot, cv2.COLOR_GRAY2BGR)
    for m in (multi if isinstance(multi, list) else ([] if multi is None else [multi])):
        try:
            x0, y0, w0, h0 = m
            cv2.rectangle(color, (x0, y0), (x0 + w0, y0 + h0), (0, 0, 255), 2)
        except Exception:
            pass
    cv2.imwrite(MATCH_OUT, color)
    print('Saved matches visualization to', MATCH_OUT)
