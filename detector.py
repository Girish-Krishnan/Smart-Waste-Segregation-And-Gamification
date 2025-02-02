import cv2
import torch
import time
import RPi.GPIO as GPIO
from transformers import BlipProcessor, BlipForConditionalGeneration
from PIL import Image

# ======================= Setup Servo Control =======================

# Define GPIO pins for servos (Update based on wiring)
SERVO_PINS = {"E-Waste": 26, "Compost": 27, "Recyclable": 22}

# Setup GPIO
GPIO.setmode(GPIO.BCM)
pwm_servos = {}

# Initialize PWM for each servo
for bin_type, pin in SERVO_PINS.items():
    GPIO.setup(pin, GPIO.OUT)
    pwm_servos[bin_type] = GPIO.PWM(pin, 50)  # 50Hz PWM
    pwm_servos[bin_type].start(0)

def set_servo(bin_type, angle):
    """Move the servo for the correct bin to the given angle (0° or 120°)."""
    if bin_type in pwm_servos:
        duty_cycle = 2 + (angle / 18)  # Convert angle to duty cycle
        pwm_servos[bin_type].ChangeDutyCycle(duty_cycle)
        time.sleep(0.5)  # Small delay for smooth movement
        pwm_servos[bin_type].ChangeDutyCycle(0)  # Stop sending PWM

# Reset all servos to 0 degrees at startup
for bin_type in SERVO_PINS:
    if bin_type=="Recyclable":
        set_servo(bin_type, 60)
    else:
        set_servo(bin_type, 0)

# ======================= Load BLIP Model =======================
device = "cuda" if torch.cuda.is_available() else "cpu"
processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base").to(device)

# ======================= OpenCV Camera =======================
cap = cv2.VideoCapture(0)  # Use 0 for default webcam

if not cap.isOpened():
    print("Error: Could not open webcam.")
    exit()

# ======================= Waste Classification Dictionary =======================
WASTE_CATEGORIES = {
    "E-Waste": [
        "electronics", "phone", "cellphone", "laptop", "computer", "tablet", "circuit", "charger",
        "adapter", "battery", "TV", "monitor", "remote", "keyboard", "mouse", "printer", "router",
        "motherboard", "hard drive", "USB drive", "earphones", "headphones", "speaker", "camera",
        "gaming console", "smartwatch", "electric toothbrush", "power bank"
    ],
    "Compost": [
        "food", "banana peel", "apple core", "vegetable", "fruit", "orange peel", "lemon peel",
        "coffee grounds", "tea bags", "egg shell", "bread", "pasta", "rice", "cooked food",
        "paper towel", "napkin", "pizza box", "leftover food", "corn husk", "biodegradable material",
        "nut shells", "compostable cup", "leaves", "grass clippings", "plant"
    ],
    "Recyclable": [
        "plastic", "bottle", "can", "glass", "aluminum", "cardboard", "paper", "magazine",
        "newspaper", "carton", "plastic container", "water bottle", "tin", "soda can",
        "foil", "jar", "milk carton", "detergent bottle", "packaging", "plastic bag",
        "styrofoam", "yogurt cup", "plastic cutlery", "plastic plate", "plastic spoon",
        "glass bottle", "glass jar", "tin can", "metal", "clothes hanger", "bubble wrap",
        "paper bag", "cereal box", "shipping box"
    ]
}

# Function to classify detected waste item
def classify_waste(description):
    description = description.lower()
    for category, items in WASTE_CATEGORIES.items():
        for item in items:
            if item in description:
                return category
    return "Unknown"  # Default if unknown item

frame_interval = 50  # Process every 50 frames (~0.66 sec at 30 FPS)
frame_count = 0

# ======================= Main Loop =======================
while True:
    ret, frame = cap.read()
    if not ret:
        print("Error: Could not read frame.")
        break

    frame_count += 1
    cv2.imwrite("test.png", frame)

    if frame_count % frame_interval == 0:
        # Convert frame to PIL Image
        image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

        # Process and predict
        inputs = processor(image, return_tensors="pt").to(device)
        inf_start = time.time()
        print("Starting generation")
        with torch.no_grad():
            output = model.generate(**inputs)
        print("End generation")
        print(time.time() - inf_start)

        description = processor.batch_decode(output, skip_special_tokens=True)[0]
        waste_bin = classify_waste(description)

        print(f"Detected: {description}")
        print(f"Recommended bin: {waste_bin}")

        # Control servo motor to open correct bin
        if waste_bin in SERVO_PINS:
            print(f"Opening {waste_bin} bin...")
            set_servo(waste_bin, 120)  # Open bin

            if waste_bin=="Compost":
                start = time.time()
                while time.time() - start < 5:
                    set_servo(waste_bin, 120)
            
            time.sleep(5)  # Keep it open for 2 seconds
            if waste_bin=="Recyclable":
                set_servo(waste_bin, 60)
            else:
                set_servo(waste_bin, 0)  # Close bin
        else:
            print("No matching bin found.")

# ======================= Cleanup =======================
cap.release()
cv2.destroyAllWindows()
for pwm in pwm_servos.values():
    pwm.stop()
GPIO.cleanup()  # Clean up GPIO resources
