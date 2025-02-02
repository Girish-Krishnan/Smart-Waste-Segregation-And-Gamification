import RPi.GPIO as GPIO
import time
import json
from flask import Flask
from flask_socketio import SocketIO
import logging
import sys
from threading import Thread
import os

# Configure logging to file and console
log_dir = os.path.dirname(os.path.abspath(__file__))
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(log_dir, 'rpi_controller.log')),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Initialize Flask and SocketIO
app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

class JoystickController:
    def __init__(self):
        try:
            # Set up GPIO using BCM numbering
            GPIO.setmode(GPIO.BCM)
            logger.info("GPIO mode set to BCM")

            # Define GPIO pins for joysticks (as per user specification)
            self.LEFT_X = 1   # Left joystick X-axis
            self.LEFT_Y = 2   # Left joystick Y-axis (not used but configured)
            self.RIGHT_X = 7  # Right joystick X-axis
            self.RIGHT_Y = 6  # Right joystick Y-axis (not used but configured)

            # Set up GPIO pins
            self.setup_gpio()
            self.test_gpio_setup()
            logger.info("GPIO pins initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize GPIO: {str(e)}")
            raise

    def setup_gpio(self):
        try:
            # Set up pins as inputs with pull-up resistors
            for pin in [self.LEFT_X, self.LEFT_Y, self.RIGHT_X, self.RIGHT_Y]:
                GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
                logger.debug(f"Set up GPIO pin {pin} as input with pull-up")
        except Exception as e:
            logger.error(f"Error setting up GPIO pins: {e}")
            raise

    def test_gpio_setup(self):
        """Test GPIO setup and log pin states"""
        for pin in [self.LEFT_X, self.LEFT_Y, self.RIGHT_X, self.RIGHT_Y]:
            try:
                value = GPIO.input(pin)
                logger.info(f"GPIO pin {pin} test read: {value}")
            except Exception as e:
                logger.error(f"Failed to read GPIO pin {pin}: {e}")
                raise

    def read_joysticks(self):
        """Read both joysticks and return normalized values"""
        try:
            # Read analog values (0 or 1 for digital input)
            left_x = GPIO.input(self.LEFT_X)
            right_x = GPIO.input(self.RIGHT_X)

            # Convert to -1 or 1 for movement
            # When button is pressed (0), move in one direction
            left_mapped = -1 if left_x == 0 else 0
            right_mapped = 1 if right_x == 0 else 0

            logger.debug(f"Joystick values - Left: {left_mapped}, Right: {right_mapped}")
            return left_mapped, right_mapped

        except Exception as e:
            logger.error(f"Error reading joysticks: {e}")
            return 0, 0

    def cleanup(self):
        try:
            GPIO.cleanup()
            logger.info("GPIO cleanup completed")
        except Exception as e:
            logger.error(f"Error during GPIO cleanup: {e}")

def read_controller():
    """Read controller values and emit through Socket.IO"""
    try:
        controller = JoystickController()
        logger.info("Controller initialized successfully")

        while True:
            try:
                left_x, right_x = controller.read_joysticks()

                # Create movement data
                movement_data = {
                    'leftJoystick': left_x,
                    'rightJoystick': right_x
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
        if 'controller' in locals():
            controller.cleanup()

if __name__ == '__main__':
    try:
        # Log GPIO version and info
        logger.info(f"RPi.GPIO Version: {GPIO.VERSION}")
        logger.info(f"Python Version: {sys.version}")

        # Start joystick reading in a separate thread
        controller_thread = Thread(target=read_controller)
        controller_thread.daemon = True
        controller_thread.start()
        logger.info("Controller thread started")

        # Run the Flask-SocketIO server
        socketio.run(app, host='0.0.0.0', port=5001, debug=True, use_reloader=False)
    except Exception as e:
        logger.error(f"Main thread error: {e}")