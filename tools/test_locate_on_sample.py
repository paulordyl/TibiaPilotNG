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
# local import of cv2 is optional; use PIL fallback for drawing if cv2 not available
try:
    import cv2
except Exception:
    cv2 = None
try:
    import numpy as np
except Exception:
    np = None

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
    # Return either a numpy ndarray (grayscale) if cv2 available, or a PIL Image (grayscale)
    if cv2 is not None:
        img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
        if img is None:
            print('Failed to read image with cv2:', path)
            sys.exit(1)
        return img
    else:
        try:
            from PIL import Image
            img = Image.open(path).convert('L')
            return img
        except Exception as e:
            print('Failed to read image with PIL:', e)
            sys.exit(1)


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
    # guard bounds and extract template depending on type
    if cv2 is not None and hasattr(screenshot, 'shape'):
        h_img, w_img = screenshot.shape
        if x < 0 or y < 0 or x + w > w_img or y + h > h_img:
            print('Template rect out of bounds for screenshot size', (w_img, h_img))
            sys.exit(1)
        template = screenshot[y:y+h, x:x+w]
        cv2.imwrite(TEMPLATE_OUT, template)
        print('Saved template to', TEMPLATE_OUT)
    else:
        # PIL Image
        from PIL import Image
        w_img, h_img = screenshot.size
        if x < 0 or y < 0 or x + w > w_img or y + h > h_img:
            print('Template rect out of bounds for screenshot size', (w_img, h_img))
            sys.exit(1)
        template_pil = screenshot.crop((x, y, x + w, y + h))
        template_pil.save(TEMPLATE_OUT)
        print('Saved template to', TEMPLATE_OUT)
        # keep template variable as None for fallback code which reloads from TEMPLATE_OUT
        template = None

    # Import locate functions from project
    PY_PATH = os.getcwd()
    if PY_PATH not in sys.path:
        sys.path.insert(0, PY_PATH)
    try:
        from src.utils.core import locate, locateMultiple
        have_project_locate = True
    except Exception as e:
        print('Project locate not available (cv2 missing?):', e)
        have_project_locate = False

    def pil_to_gray_array(pil_img):
        # returns 2D list of pixel ints
        gray = pil_img.convert('L')
        w, h = gray.size
        px = list(gray.getdata())
        # convert to rows
        rows = [px[i * w:(i + 1) * w] for i in range(h)]
        return rows

    def locate_fallback(full_img_path, template_img, confidence=0.85):
        # exact-match fallback using PIL pixel comparison; confidence ignored (exact only)
        try:
            from PIL import Image
            full = Image.open(full_img_path).convert('L')
        except Exception as e:
            print('Fallback locate: failed to open full image via PIL:', e)
            return None
        full_a = pil_to_gray_array(full)
        templ_a = pil_to_gray_array(Image.fromarray(template)) if 'numpy' in globals() and template is not None and not isinstance(template, str) else None
        # template is currently a numpy array if cv2 was available; but in our flow template was saved to disk earlier, so just reload it
        try:
            templ = Image.open(TEMPLATE_OUT).convert('L')
            t_w, t_h = templ.size
            templ_px = list(templ.getdata())
            templ_rows = [templ_px[i * t_w:(i + 1) * t_w] for i in range(t_h)]
        except Exception as e:
            print('Fallback locate: failed to load template via PIL:', e)
            return None

        H = len(full_a)
        W = len(full_a[0])
        h_t = len(templ_rows)
        w_t = len(templ_rows[0])
        for y in range(0, H - h_t + 1):
            for x in range(0, W - w_t + 1):
                match = True
                for ty in range(h_t):
                    row_full = full_a[y + ty]
                    row_templ = templ_rows[ty]
                    # quick slice compare
                    if row_full[x:x + w_t] != row_templ:
                        match = False
                        break
                if match:
                    return (x, y, w_t, h_t)
        return None

    def locateMultiple_fallback(full_img_path, template_img, confidence=0.85):
        single = locate_fallback(full_img_path, template_img, confidence)
        return [single] if single else []

    print('Running locate (single-match)')
    if have_project_locate:
        try:
            res = locate(screenshot, template, confidence=0.7)
        except Exception as e:
            print('locate threw exception:', e)
            res = None
    else:
        print('Using fallback exact-match locate (may miss near-matches).')
        res = locate_fallback(SSHOT, TEMPLATE_OUT, confidence=0.7)
    print('locate result:', res)

    print('\nRunning locateMultiple (all matches >= confidence)')
    if have_project_locate:
        try:
            multi = locateMultiple(screenshot, template, confidence=0.7)
        except Exception as e:
            print('locateMultiple threw exception:', e)
            multi = []
    else:
        multi = locateMultiple_fallback(SSHOT, TEMPLATE_OUT, confidence=0.7)
    print('Found matches count:', len(multi))
    for m in multi[:20]:
        print('  match:', m)

    # Draw rectangles on a color copy to visualize
    if cv2 is not None:
        color = cv2.cvtColor(screenshot, cv2.COLOR_GRAY2BGR)
        for m in (multi if isinstance(multi, list) else ([] if multi is None else [multi])):
            try:
                x0, y0, w0, h0 = m
                cv2.rectangle(color, (x0, y0), (x0 + w0, y0 + h0), (0, 0, 255), 2)
            except Exception:
                pass
        cv2.imwrite(MATCH_OUT, color)
        print('Saved matches visualization to', MATCH_OUT)
    else:
        # Use PIL for drawing if cv2 not available
        try:
            from PIL import Image, ImageDraw
            pil_img = Image.open(SSHOT).convert('RGB')
            draw = ImageDraw.Draw(pil_img)
            for m in (multi if isinstance(multi, list) else ([] if multi is None else [multi])):
                try:
                    x0, y0, w0, h0 = m
                    draw.rectangle([x0, y0, x0 + w0, y0 + h0], outline=(255, 0, 0), width=3)
                except Exception:
                    pass
            pil_img.save(MATCH_OUT)
            print('Saved matches visualization to', MATCH_OUT)
        except Exception as e:
            print('No cv2 or PIL available to draw matches:', e)
            print('Skipping matches visualization')
