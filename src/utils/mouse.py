import pyautogui
from src.shared.typings import XYCoordinate

def drag(x1y1: XYCoordinate, x2y2: XYCoordinate):
    pyautogui.moveTo(x1y1[0], x1y1[1], duration=0.2, tween=pyautogui.easeInOutQuad)
    pyautogui.mouseDown()
    pyautogui.moveTo(x2y2[0], x2y2[1], duration=0.3, tween=pyautogui.easeInOutQuad)
    pyautogui.mouseUp()

def leftClick(windowCoordinate: XYCoordinate = None):
    if windowCoordinate:
        pyautogui.moveTo(windowCoordinate[0], windowCoordinate[1], duration=0.2, tween=pyautogui.easeInOutQuad)
    pyautogui.click()

def moveTo(windowCoordinate: XYCoordinate):
    pyautogui.moveTo(windowCoordinate[0], windowCoordinate[1], duration=0.2, tween=pyautogui.easeInOutQuad)

def rightClick(windowCoordinate: XYCoordinate = None):
    if windowCoordinate:
        pyautogui.moveTo(windowCoordinate[0], windowCoordinate[1], duration=0.2, tween=pyautogui.easeInOutQuad)
    pyautogui.click(button='right')

def scroll(clicks: int):
    pyautogui.scroll(clicks)
