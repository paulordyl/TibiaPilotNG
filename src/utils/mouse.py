import pyautogui
from src.shared.typings import XYCoordinate
from .ino import sendCommandArduino

def drag(x1y1: XYCoordinate, x2y2: XYCoordinate):
    sendCommandArduino(f"moveTo,{int(x1y1[0])},{int(x1y1[1])}")
    sendCommandArduino("dragStart")
    sendCommandArduino(f"moveTo,{int(x2y2[0])},{int(x2y2[1])}")
    sendCommandArduino("dragEnd")

def leftClick(windowCoordinate: XYCoordinate = None):
    if windowCoordinate is None:
        sendCommandArduino("leftClick")
        return
    sendCommandArduino(f"moveTo,{int(windowCoordinate[0])},{int(windowCoordinate[1])}")
    sendCommandArduino("leftClick")

def moveTo(windowCoordinate: XYCoordinate):
    sendCommandArduino(f"moveTo,{int(windowCoordinate[0])},{int(windowCoordinate[1])}")

def rightClick(windowCoordinate: XYCoordinate = None):
    if windowCoordinate is None:
        sendCommandArduino("rightClick")
        return
    sendCommandArduino(f"moveTo,{int(windowCoordinate[0])},{int(windowCoordinate[1])}")
    sendCommandArduino("rightClick")

def scroll(clicks: int):
    curX, curY = pyautogui.position()
    sendCommandArduino(f"scroll,{curX}, {curY}, {clicks}")
