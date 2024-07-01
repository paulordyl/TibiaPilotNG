#include <Wire.h>
#include <ArduinoJson.h>
#include <AbsMouse.h>
#include <hiduniversal.h>
#include "hidmouserptparser.h"

// ACTION LIST
// 0 -> moveTo (a, x, y)
// 1 -> moveToAndClick (a, x, y)
// 2 -> moveToAndRightClick (a, x, y)
// 3 -> dragTo (a, x, y)
// 4 -> pressMiddle (a, x = 0, y = 0)
// 5 -> updateMousePosition (a, x, y)

int currentMouseX = 0;
int currentMouseY = 0;

int new_width = 1920;
int new_height = 1080;

int old_width = 1366;
int old_height = 768;

USB Usb;
HIDUniversal Hid(&Usb);
HIDMouseReportParser Mou(nullptr);

float lerp(float a, float b, float t) {
  return a + t * (b - a);
}

void smooth_move(int steps, int delayTime, int targetX, int targetY) {
  int x_new = (int)((targetX * new_width) / old_width);
  int y_new = (int)((targetY * new_height) / old_height);

  for (int i = 1; i <= steps; i++) {
    float t = i / float(steps);

    int x = lerp(currentMouseX, x_new, t);
    int y = lerp(currentMouseY, y_new, t);

    // Movimento suavizado do mouse
    AbsMouse.move(x, y);
    currentMouseX = x;
    currentMouseY = y;

    delay(delayTime);  // Ajuste o atraso conforme necessário para suavizar o movimento
  }
}

void receiveEvent(uint8_t byteCount) {
  // Ler os dados JSON da I2C
  String receivedString = "";
  while (Wire.available()) {
    char c = Wire.read();
    receivedString += c;
  }

  // Parse JSON
  DynamicJsonDocument doc(200);
  DeserializationError error = deserializeJson(doc, receivedString);

  if (!error) {
    int a = doc["a"];
    int x = doc["x"];
    int y = doc["y"];

    if (a == 0) {
      smooth_move(1000, 20, x, y);
    } else if (a == 1) {
      smooth_move(1000, 20, x, y);
      AbsMouse.press(MOUSE_LEFT);
      AbsMouse.release(MOUSE_LEFT);
    } else if (a == 2) {
      smooth_move(1000, 20, x, y);
      AbsMouse.press(MOUSE_RIGHT);
      AbsMouse.release(MOUSE_RIGHT);
    } else if (a == 3) {
      AbsMouse.press(MOUSE_LEFT);
      smooth_move(1000, 20, x, y);
      AbsMouse.release(MOUSE_LEFT);
    } else if (a == 4) {
      AbsMouse.press(MOUSE_MIDDLE);
      AbsMouse.release(MOUSE_MIDDLE);
    } else if (a == 5) {
      currentMouseX = x;
      currentMouseY = y;
    }
  } else {
    // Serial.print("Error parsing JSON: ");
    // Serial.println(error.c_str());
  }
}

void setup() {
  Wire.begin(8);  // I2C Address
  Wire.onReceive(receiveEvent);
  // Serial.begin(115200);
  AbsMouse.init(1920, 1080);

  if (Usb.Init() == -1)
		// Serial.println("OSC did not start.");
	
	delay(200);

	if (!Hid.SetReportParser(0, &Mou))
		ErrorMessage<uint8_t > (PSTR("SetReportParser"), 1);
}

void loop() {
  Usb.Task();
}

void onButtonDown(uint16_t buttonId) {
	AbsMouse.press(buttonId);
	// Serial.print("Button ");
	switch (buttonId) {
		case MOUSE_LEFT:
			// Serial.print("MOUSE_LEFT");
			break;

		case MOUSE_RIGHT:
			// Serial.print("MOUSE_RIGHT");
			break;
		
		case MOUSE_MIDDLE:
			// Serial.print("MOUSE_MIDDLE");
			break;

		case MOUSE_BUTTON4:
			// Serial.print("MOUSE_BUTTON4");
			break;

		case MOUSE_BUTTON5:
			// Serial.print("MOUSE_BUTTON5");
			break;
		default:
			// Serial.print("OTHER_BUTTON");
			break;
	}
	// Serial.println(" pressed");
}

void onButtonUp(uint16_t buttonId) {
	AbsMouse.release(buttonId);
	Serial.print("Button ");
	switch (buttonId) {
		case MOUSE_LEFT:
			// Serial.print("MOUSE_LEFT");
			break;

		case MOUSE_RIGHT:
			// Serial.print("MOUSE_RIGHT");
			break;
		
		case MOUSE_MIDDLE:
			// Serial.print("MOUSE_MIDDLE");
			break;

		case MOUSE_BUTTON4:
			// Serial.print("MOUSE_BUTTON4");
			break;

		case MOUSE_BUTTON5:
			// Serial.print("MOUSE_BUTTON5");
			break;
		default:
			// Serial.print("OTHER_BUTTON");
			break;
	}
	Serial.println(" released");
}

void onTiltPress(int8_t tiltValue) {
	// Serial.print("Tilt pressed: ");
	// Serial.println(tiltValue);
}

void onMouseMove(int8_t xMovement, int8_t yMovement, int8_t scrollValue) {
  currentMouseX += xMovement;
  currentMouseY += yMovement;
	AbsMouse.move(currentMouseX, currentMouseY);
	// Serial.print("Mouse moved:\t");
	// Serial.print(xMovement);
	// Serial.print("\t");
	// Serial.print(yMovement);
	// Serial.print("\t");
	// Serial.println(scrollValue);
}