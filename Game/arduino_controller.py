import serial
import logging
import sys
from flask import Flask
from flask_socketio import SocketIO
import time
from threading import Thread

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('arduino_controller.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Initialize Flask and SocketIO
app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

class ArduinoController:
    def __init__(self, port='/dev/ttyUSB0', baudrate=9600):
        try:
            self.serial = serial.Serial(port, baudrate, timeout=1)
            logger.info(f"Connected to Arduino on {port}")
            time.sleep(2)  # Wait for Arduino to reset
        except Exception as e:
            logger.error(f"Failed to connect to Arduino: {str(e)}")
            raise

    def read_joystick(self):
        """Read joystick value from Arduino"""
        try:
            if self.serial.in_waiting:
                value = self.serial.readline().decode().strip()
                try:
                    return int(value)  # Convert to integer (-1, 0, or 1)
                except ValueError:
                    logger.warning(f"Invalid value received: {value}")
            return 0
        except Exception as e:
            logger.error(f"Error reading from Arduino: {str(e)}")
            return 0

    def cleanup(self):
        """Close the serial connection"""
        try:
            if hasattr(self, 'serial'):
                self.serial.close()
                logger.info("Serial connection closed")
        except Exception as e:
            logger.error(f"Error during cleanup: {str(e)}")

def read_controller():
    """Read controller values and emit through Socket.IO"""
    try:
        # Try different USB ports
        ports = ['/dev/ttyUSB0', '/dev/ttyUSB1', '/dev/ttyACM0', '/dev/ttyACM1']
        controller = None
        
        for port in ports:
            try:
                controller = ArduinoController(port=port)
                logger.info(f"Successfully connected to Arduino on {port}")
                break
            except:
                continue
                
        if not controller:
            logger.error("Could not connect to Arduino on any port")
            return

        while True:
            try:
                movement = controller.read_joystick()
                
                # Create movement data
                movement_data = {
                    'leftJoystick': movement,  # Use same value for both since we only have one joystick
                    'rightJoystick': 0         # Not used with single joystick setup
                }
                
                # Emit the data through Socket.IO
                socketio.emit('joystick_input', movement_data)
                time.sleep(0.05)  # 50ms delay to prevent flooding
                
            except Exception as e:
                logger.error(f"Error in controller loop: {e}")
                time.sleep(1)  # Wait before retrying

    except Exception as e:
        logger.error(f"Failed to initialize controller: {e}")
    finally:
        if controller:
            controller.cleanup()

if __name__ == '__main__':
    try:
        # Start controller reading in a separate thread
        controller_thread = Thread(target=read_controller)
        controller_thread.daemon = True
        controller_thread.start()
        logger.info("Controller thread started")

        # Run the Flask-SocketIO server
        socketio.run(app, host='0.0.0.0', port=5001, debug=True, use_reloader=False)
    except Exception as e:
        logger.error(f"Main thread error: {e}")
