import time # Added for sleeps in hotkey, press, write
from .ino_rs import ArduinoComm, ArduinoCommError # New import

# Initialize Arduino communication
# TODO: Port name should ideally be configurable, not hardcoded.
# For now, using the port from the original ino.py.
# The actual library path for libarduino_comm.so/dll will be resolved by ArduinoComm itself.
try:
    arduino_comm = ArduinoComm("COM33") 
except ArduinoCommError as e:
    print(f"Failed to initialize Arduino communication for keyboard: {e}")
    # Fallback or dummy object if critical, or let it raise if arduino is essential
    # For now, if it fails, subsequent calls will fail.
    # A more robust app might have a dummy_arduino_comm that logs or no-ops.
    arduino_comm = None # Or a dummy object

def getAsciiFromKey(key):
    if not key:
        return 0

    sanitized = key.lower()

    if sanitized == '?':
        return 63

    if sanitized.isalpha() and len(sanitized) == 1:
        return ord(sanitized)
    
    if sanitized == 'space':
        return 32
    elif sanitized == 'esc':
        return 177
    elif sanitized == 'ctrl':
        return 128
    elif sanitized == 'alt':
        return 130
    elif sanitized == 'shift':
        return 129
    elif sanitized == 'enter':
        return 176
    elif sanitized == 'up':
        return 218
    elif sanitized == 'down':
        return 217
    elif sanitized == 'left':
        return 216
    elif sanitized == 'right':
        return 215
    elif sanitized == 'backspace':
        return 178
    elif sanitized == 'f1':
        return 194
    elif sanitized == 'f2':
        return 195
    elif sanitized == 'f3':
        return 196
    elif sanitized == 'f4':
        return 197
    elif sanitized == 'f5':
        return 198
    elif sanitized == 'f6':
        return 199
    elif sanitized == 'f7':
        return 200
    elif sanitized == 'f8':
        return 201
    elif sanitized == 'f9':
        return 202
    elif sanitized == 'f10':
        return 203
    elif sanitized == 'f11':
        return 204
    elif sanitized == 'f12':
        return 205
    else:
        return 0

def hotkey(*args, interval: float = 0.01): # Added interval based on original ino.py
    if not arduino_comm:
        print("Arduino communication not initialized for keyboard (hotkey).")
        return
    
    try:
        for key in args:
            asciiKey = getAsciiFromKey(key)
            if asciiKey != 0:
                raw_command_down = f"keyDown,{asciiKey}"
                arduino_comm.send(raw_command_down)
        
        time.sleep(interval) # Sleep between all downs and all ups

        for key in args:
            asciiKey = getAsciiFromKey(key)
            if asciiKey != 0:
                raw_command_up = f"keyUp,{asciiKey}"
                arduino_comm.send(raw_command_up)
    except ArduinoCommError as e:
        print(f"Error sending hotkey command: {e}")


def keyDown(key: str):
    if not arduino_comm:
        print("Arduino communication not initialized for keyboard (keyDown).")
        return
        
    asciiKey = getAsciiFromKey(key)
    if asciiKey != 0:
        raw_command = f"keyDown,{asciiKey}"
        try:
            arduino_comm.send(raw_command)
        except ArduinoCommError as e:
            print(f"Error sending keyDown command: {e}")

def keyUp(key: str):
    if not arduino_comm:
        print("Arduino communication not initialized for keyboard (keyUp).")
        return

    asciiKey = getAsciiFromKey(key)
    if asciiKey != 0:
        raw_command = f"keyUp,{asciiKey}"
        try:
            arduino_comm.send(raw_command)
        except ArduinoCommError as e:
            print(f"Error sending keyUp command: {e}")

def press(*args, duration: float = 0.05): # Added duration based on original ino.py
    if not arduino_comm:
        print("Arduino communication not initialized for keyboard (press).")
        return

    try:
        for key in args:
            asciiKey = getAsciiFromKey(key)
            if asciiKey != 0:
                raw_command = f"press,{asciiKey}"
                arduino_comm.send(raw_command)
                # The sleep for 'press' in original ino.py was after arduinoSerial.write()
                # and specific to each key press in the loop.
                time.sleep(duration) 
    except ArduinoCommError as e:
        print(f"Error sending press command: {e}")

def write(phrase: str, delayBetweenPresses: float = 0.01): # Added delay based on original ino.py
    if not arduino_comm:
        print("Arduino communication not initialized for keyboard (write).")
        return

    raw_command = f"write,{phrase}"
    try:
        arduino_comm.send(raw_command)
        # The sleep for 'write' in original ino.py was after arduinoSerial.write()
        time.sleep(delayBetweenPresses * len(phrase)) 
    except ArduinoCommError as e:
        print(f"Error sending write command: {e}")
