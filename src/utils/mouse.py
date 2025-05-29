import pyautogui
from src.shared.typings import XYCoordinate
from .ino_rs import ArduinoComm, ArduinoCommError # New import

# Initialize Arduino communication
# TODO: Port name should ideally be configurable.
# Using the same port as specified for keyboard.
try:
    arduino_comm = ArduinoComm("COM33") 
except ArduinoCommError as e:
    print(f"Failed to initialize Arduino communication for mouse: {e}")
    arduino_comm = None # Fallback or dummy object

def drag(x1y1: XYCoordinate, x2y2: XYCoordinate):
    if arduino_comm:
        try:
            # Call moveTo which has its own error handling and arduino_comm check
            moveTo(x1y1) 
            arduino_comm.send("dragStart")
            # Call moveTo which has its own error handling and arduino_comm check
            moveTo(x2y2) 
            arduino_comm.send("dragEnd")
        except ArduinoCommError as e:
            print(f"Error during drag operation: {e}")
    elif arduino_comm is not None: # Only print if initialization was attempted but failed
        print("Arduino communication not initialized for mouse (drag).")


def leftClick(windowCoordinate: XYCoordinate = None):
    if arduino_comm:
        try:
            if windowCoordinate is not None:
                # Call moveTo which has its own error handling and arduino_comm check
                moveTo(windowCoordinate)
            arduino_comm.send("leftClick")
        except ArduinoCommError as e:
            print(f"Error sending leftClick command: {e}")
    elif arduino_comm is not None:
        print("Arduino communication not initialized for mouse (leftClick).")


def moveTo(windowCoordinate: XYCoordinate):
    if arduino_comm:
        raw_command = f"moveTo,{int(windowCoordinate[0])},{int(windowCoordinate[1])}"
        try:
            arduino_comm.send(raw_command)
        except ArduinoCommError as e:
            print(f"Error sending moveTo command: {e}")
    elif arduino_comm is not None: # Only print if initialization was attempted but failed
         print("Arduino communication not initialized for mouse (moveTo).")


def rightClick(windowCoordinate: XYCoordinate = None):
    if arduino_comm:
        try:
            if windowCoordinate is not None:
                # Call moveTo which has its own error handling and arduino_comm check
                moveTo(windowCoordinate)
            arduino_comm.send("rightClick")
        except ArduinoCommError as e:
            print(f"Error sending rightClick command: {e}")
    elif arduino_comm is not None:
        print("Arduino communication not initialized for mouse (rightClick).")


def scroll(clicks: int):
    if arduino_comm:
        # pyautogui.position() remains for now
        curX, curY = pyautogui.position() 
        raw_command = f"scroll,{curX},{curY},{clicks}" # Note: original f-string had a space after {curY}, removed for consistency.
        try:
            arduino_comm.send(raw_command)
        except ArduinoCommError as e:
            print(f"Error sending scroll command: {e}")
    elif arduino_comm is not None:
        print("Arduino communication not initialized for mouse (scroll).")
