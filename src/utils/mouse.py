import pyautogui
import random
import time
from pyautogui import easeInOutQuad, easeInQuad, easeOutQuad, linear
from src.shared.typings import XYCoordinate

TWEEN_FUNCTIONS = [easeInOutQuad, easeInQuad, easeOutQuad, linear]

def drag(x1y1: XYCoordinate, x2y2: XYCoordinate):
    duration1 = random.uniform(0.15, 0.35)
    tween1 = random.choice(TWEEN_FUNCTIONS)
    pyautogui.moveTo(x1y1[0], x1y1[1], duration=duration1, tween=tween1)
    pyautogui.mouseDown()
    duration2 = random.uniform(0.2, 0.4)
    tween2 = random.choice(TWEEN_FUNCTIONS)
    pyautogui.moveTo(x2y2[0], x2y2[1], duration=duration2, tween=tween2)
    pyautogui.mouseUp()

def leftClick(windowCoordinate: XYCoordinate = None):
    if windowCoordinate:
        duration = random.uniform(0.15, 0.35)
        tween = random.choice(TWEEN_FUNCTIONS)
        pyautogui.moveTo(windowCoordinate[0], windowCoordinate[1], duration=duration, tween=tween)
    pyautogui.mouseDown(button='left')
    time.sleep(random.uniform(0.04, 0.08))
    pyautogui.mouseUp(button='left')

def moveTo(windowCoordinate: XYCoordinate):
    duration = random.uniform(0.15, 0.35)
    tween = random.choice(TWEEN_FUNCTIONS)
    pyautogui.moveTo(windowCoordinate[0], windowCoordinate[1], duration=duration, tween=tween)

def rightClick(windowCoordinate: XYCoordinate = None):
    if windowCoordinate:
        duration = random.uniform(0.15, 0.35)
        tween = random.choice(TWEEN_FUNCTIONS)
        pyautogui.moveTo(windowCoordinate[0], windowCoordinate[1], duration=duration, tween=tween)
    pyautogui.mouseDown(button='right')
    time.sleep(random.uniform(0.04, 0.08))
    pyautogui.mouseUp(button='right')

def scroll(clicks: int):
    pyautogui.scroll(clicks)
