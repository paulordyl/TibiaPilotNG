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
        # If the environment requests simulation, attempt to execute equivalent
        # mouse actions locally via pyautogui so users can test OBS/capture flows
        # without the physical Arduino device. Enable with ARDUINO_SIMULATE_WITH_PYAUTOGUI=1.
        if os.getenv('ARDUINO_SIMULATE_WITH_PYAUTOGUI') == '1':
            try:
                import pyautogui
            except Exception:
                print('ARDUINO_SIMULATE_WITH_PYAUTOGUI set but pyautogui is not installed. Install with: pip install pyautogui')
                return
            parts = command.split(',')
            cmd = parts[0] if len(parts) > 0 else ''
            try:
                if cmd == 'moveTo' and len(parts) >= 3:
                    x = int(float(parts[1])); y = int(float(parts[2]))
                    pyautogui.moveTo(x, y)
                elif cmd == 'leftClick':
                    if len(parts) >= 3:
                        x = int(float(parts[1])); y = int(float(parts[2]))
                        pyautogui.click(x, y, button='left')
                    else:
                        pyautogui.click()
                elif cmd == 'rightClick':
                    if len(parts) >= 3:
                        x = int(float(parts[1])); y = int(float(parts[2]))
                        pyautogui.click(x, y, button='right')
                    else:
                        pyautogui.click(button='right')
                elif cmd == 'dragStart' or cmd == 'dragEnd':
                    # drag events are no-ops in simple simulation; higher-level code uses moveTo + drag commands
                    pass
                elif cmd == 'scroll' and len(parts) >= 4:
                    clicks = int(float(parts[3]))
                    pyautogui.scroll(clicks)
                else:
                    print(f'Unrecognized Arduino simulated command: {command}')
            except Exception as e:
                print('Error simulating Arduino command:', e)
            return
        # Default: no-op when Arduino serial is unavailable (useful for CI and local dev without hardware)
        return
    commandBytes = command.encode('utf-8')
    commandBase64 = base64.b64encode(commandBytes).decode('utf-8') + '\n'
    arduinoSerial.write(commandBase64.encode())
    sleep(0.01)