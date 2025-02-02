# Nothing's Working: How To Throw Things Away

A fun waste management game that teaches proper recycling through Space Invaders-style gameplay.

## Local Setup with Arduino Controls

### Requirements
- Python 3.11+
- Arduino Uno/Nano/Pro Mini
- 1 analog joystick
- Jumper wires
- Mac OS X, Linux, or Windows for the game server
- Arduino IDE (for uploading the controller sketch)

### Hardware Setup
1. Connect the joystick to Arduino:
   ```
   Joystick:
   - X-axis -> A0
   - VCC -> 5V
   - GND -> GND
   ```

### Quick Setup
1. Clone or download this repository
2. Run the setup script:
```bash
chmod +x setup.sh
./setup.sh
```

### Arduino Setup
1. Open Arduino IDE
2. Load the sketch from `arduino_sketch/waste_controller/waste_controller.ino`
3. Select your Arduino board and port
4. Upload the sketch

### Running the Game
1. Open two terminal windows
2. In the first terminal, start the game server:
```bash
python3 main.py
```
3. In the second terminal, start the Arduino controller:
```bash
python3 arduino_controller.py
```
4. Open your browser and visit:
```
http://localhost:5000
```

### Controls
- **Keyboard** (fallback): Left/Right arrow keys or A/D keys
- **Arduino Joystick**: 
  - Move stick left/right to control the bin
- **Gameplay**: 
  - Catch items matching the current category shown at top
  - Glowing items are the ones you should catch!

### Troubleshooting Arduino Issues
1. Check the controller logs:
```bash
tail -f arduino_controller.log
```

2. Verify Arduino connection:
```bash
ls /dev/tty*
# Look for /dev/ttyUSB* or /dev/ttyACM*
```

3. Common issues:
   - Permission denied: Add user to dialout group
     ```bash
     sudo usermod -a -G dialout $USER
     # Log out and back in
     ```
   - Arduino not detected: Check USB cable and port
   - Erratic movement: Check joystick connections
   - No response: Verify sketch uploaded successfully

### Game Rules
- Match falling items with the current category
- Score points for correct catches
- Avoid wrong items to maintain accuracy
- Watch your environmental impact score grow!