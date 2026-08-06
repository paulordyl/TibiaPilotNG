import serial
from time import sleep
import base64
import os

# Initialize serial connection if available. On platforms without the Arduino
# attached (or during tests), fail gracefully by setting arduinoSerial to None.
arduinoSerial = None
try:
    port = os.getenv('ARDUINO_PORT', 'COM33')
    arduinoSerial = serial.Serial(port, 115200, timeout=1)
except Exception:
    arduinoSerial = None


def sendCommandArduino(command):
    if arduinoSerial is None:
        # No-op when Arduino serial is unavailable (useful for CI and local dev without hardware)
        return
    commandBytes = command.encode('utf-8')
    commandBase64 = base64.b64encode(commandBytes).decode('utf-8') + '\n'
    arduinoSerial.write(commandBase64.encode())
    sleep(0.01)