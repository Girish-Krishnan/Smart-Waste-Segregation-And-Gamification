import RPi.GPIO as GPIO
import time
import sys

def test_gpio_pins():
    """Test GPIO pins for joystick connections"""
    try:
        # Set up GPIO using BCM numbering
        GPIO.setmode(GPIO.BCM)
        print(f"RPi.GPIO Version: {GPIO.VERSION}")
        print(f"Python Version: {sys.version}")
        
        # Define pins
        LEFT_X = 1   # Left joystick X-axis
        RIGHT_X = 7  # Right joystick X-axis
        
        # Set up pins
        GPIO.setup(LEFT_X, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(RIGHT_X, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        
        print("\nTesting joystick connections...")
        print("Press Ctrl+C to exit")
        print("\nMove each joystick and watch the values change:")
        
        while True:
            left = GPIO.input(LEFT_X)
            right = GPIO.input(RIGHT_X)
            print(f"\rLeft Joystick: {'Pressed' if left == 0 else 'Released'} | "
                  f"Right Joystick: {'Pressed' if right == 0 else 'Released'}", end='')
            time.sleep(0.1)
            
    except KeyboardInterrupt:
        print("\n\nTest completed.")
    except Exception as e:
        print(f"\nError: {str(e)}")
    finally:
        GPIO.cleanup()

if __name__ == "__main__":
    test_gpio_pins()
