#!/bin/bash

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is required but not installed. Please install Python 3 first."
    exit 1
fi

# Check if pip3 is available, if not try to use python3 -m pip
PIP_CMD=""
if command -v pip3 &> /dev/null; then
    PIP_CMD="pip3"
elif python3 -m pip --version &> /dev/null; then
    PIP_CMD="python3 -m pip"
else
    echo "pip3 not found. Please install pip for Python 3:"
    echo "python3 -m ensurepip --upgrade"
    exit 1
fi

# Install required Python packages
echo "Installing required Python packages..."
$PIP_CMD install flask flask-socketio pyserial || {
    echo "Failed to install packages. Try running:"
    echo "sudo $PIP_CMD install flask flask-socketio pyserial"
    exit 1
}

# Verify installation
echo "Verifying installation..."
python3 -c "import flask; import flask_socketio; import serial; print('All dependencies installed successfully!')" || {
    echo "Verification failed. Please check the error messages above."
    exit 1
}

# Print success message with color
GREEN='\033[0;32m'
NC='\033[0m' # No Color
echo -e "${GREEN}Setup complete!${NC}"
echo ""
echo "To run the game:"
echo "1. Upload the Arduino sketch in arduino_sketch/waste_controller/"
echo "2. In one terminal window run: python3 main.py"
echo "3. In another terminal window run: python3 arduino_controller.py"
echo "4. Open your browser and visit: http://localhost:5000"
echo ""
echo "Make sure your Arduino is connected and the joystick is properly wired!"