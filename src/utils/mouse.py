import pyautogui
import random
import time
from pyautogui import easeInOutQuad, easeInQuad, easeOutQuad, linear
from src.shared.typings import XYCoordinate

TWEEN_FUNCTIONS = [easeInOutQuad, easeInQuad, easeOutQuad, linear]

def _apply_random_offset(coord: XYCoordinate, offset_range: int = 1) -> XYCoordinate:
    if coord is None:
        return None
    offset_x = random.randint(-offset_range, offset_range)
    offset_y = random.randint(-offset_range, offset_range)
    return (coord[0] + offset_x, coord[1] + offset_y)

def drag(x1y1: XYCoordinate, x2y2: XYCoordinate):
    start_coord = _apply_random_offset(x1y1, 1)
    end_coord = _apply_random_offset(x2y2, 1)
    if start_coord is None or end_coord is None:
        # Fallback or error, though drag implies valid coords
        return

    duration1 = random.uniform(0.15, 0.35)
    tween1 = random.choice(TWEEN_FUNCTIONS)
    pyautogui.moveTo(start_coord[0], start_coord[1], duration=duration1, tween=tween1)
    pyautogui.mouseDown()
    duration2 = random.uniform(0.2, 0.4)
    tween2 = random.choice(TWEEN_FUNCTIONS)
    pyautogui.moveTo(end_coord[0], end_coord[1], duration=duration2, tween=tween2)
    pyautogui.mouseUp()

def leftClick(windowCoordinate: XYCoordinate = None):
    target_coord = _apply_random_offset(windowCoordinate, 1)
    if target_coord: # Check if target_coord is not None (it could be if windowCoordinate was None)
        duration = random.uniform(0.15, 0.35)
        tween = random.choice(TWEEN_FUNCTIONS)
        pyautogui.moveTo(target_coord[0], target_coord[1], duration=duration, tween=tween)
    # If windowCoordinate was None, target_coord will be None, and no move occurs. Click at current position.
    pyautogui.mouseDown(button='left')
    time.sleep(random.uniform(0.04, 0.08))
    pyautogui.mouseUp(button='left')

def moveTo(windowCoordinate: XYCoordinate):
    target_coord = _apply_random_offset(windowCoordinate, 1)
    if target_coord is None: # Should not happen if windowCoordinate is guaranteed by type, but good practice
        return

    duration = random.uniform(0.15, 0.35)
    tween = random.choice(TWEEN_FUNCTIONS)
    pyautogui.moveTo(target_coord[0], target_coord[1], duration=duration, tween=tween)

def rightClick(windowCoordinate: XYCoordinate = None):
    target_coord = _apply_random_offset(windowCoordinate, 1)
    if target_coord:
        duration = random.uniform(0.15, 0.35)
        tween = random.choice(TWEEN_FUNCTIONS)
        pyautogui.moveTo(target_coord[0], target_coord[1], duration=duration, tween=tween)
    pyautogui.mouseDown(button='right')
    time.sleep(random.uniform(0.04, 0.08))
    pyautogui.mouseUp(button='right')

def scroll(clicks: int):
    pyautogui.scroll(clicks)
