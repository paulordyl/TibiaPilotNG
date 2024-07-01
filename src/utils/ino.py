import serial
from time import sleep
import base64

arduinoSerial = serial.Serial('COM33', 115200, timeout=1)

def sendCommandArduino(command):
    commandBytes = command.encode('utf-8')
    commandBase64 = base64.b64encode(commandBytes).decode('utf-8') + '\n'
    arduinoSerial.write(commandBase64.encode())
    sleep(0.01)