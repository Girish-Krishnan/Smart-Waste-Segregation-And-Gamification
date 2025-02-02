// Waste Management Game - Arduino Controller
// Uses a single joystick for movement

const int JOY_X = A0;  // X-axis pin
const int JOY_Y = A1;  // Y-axis pin (not used but configured)

// Center position calibration
const int CENTER_THRESHOLD = 100;  // Deadzone for center position
const int CENTER_VALUE = 512;      // Middle value for analog read

void setup() {
  Serial.begin(9600);  // Start serial communication
}

void loop() {
  // Read joystick values
  int xValue = analogRead(JOY_X);
  
  // Calculate movement (-1, 0, or 1)
  int movement = 0;
  
  // Convert analog value to movement
  if (abs(xValue - CENTER_VALUE) > CENTER_THRESHOLD) {
    movement = (xValue > CENTER_VALUE) ? 1 : -1;
  }
  
  // Send movement value over serial
  Serial.println(movement);
  
  // Small delay to prevent serial buffer overflow
  delay(50);
}
