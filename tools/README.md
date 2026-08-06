Tools for OBS / mouse / locate testing

Quick reference

1. Run the demo mouse script (moves your system cursor):
   PYTHONPATH=$(pwd) python3 tools/test_obs_mouse.py

2. Capture a screenshot (uses project dxcam or falls back to pyautogui):
   PYTHONPATH=$(pwd) python3 tools/capture_screenshot.py
   - Saves tools/latest_screenshot.png

3. Create a template region and test locate():
   - Option A: provide coords on the command line (x y w h):
       PYTHONPATH=$(pwd) python3 tools/test_locate_on_sample.py 100 200 50 50
   - Option B: set TEMPLATE_RECT env var: "100,200,50,50"
       PYTHONPATH=$(pwd) TEMPLATE_RECT="100,200,50,50" python3 tools/test_locate_on_sample.py

Outputs:
- tools/latest_screenshot.png (grayscale)
- tools/template.png (grayscale crop)
- tools/matches.png (screenshot annotated with rectangles for matches)

Notes:
- Ensure macOS permissions: Terminal must have Accessibility / Input Monitoring to allow pyautogui mouse control.
- For image-based locate testing, start OBS display capture so tests reflect the captured pixels.
- Use ARDUINO_SIMULATE_WITH_PYAUTOGUI=1 to simulate mouse commands via pyautogui.
