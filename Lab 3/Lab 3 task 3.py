from machine import Pin, PWM
import time

# ==========================
# IR Sensor
# ==========================
ir = Pin(12, Pin.IN)

# ==========================
# Servo Motor
# ==========================
servo = PWM(Pin(13), freq=50)

def set_angle(angle):
    # Convert angle (0-180) to PWM duty
    duty = int((angle / 180) * 102 + 26)
    servo.duty(duty)

# Start with gate closed
set_angle(0)

print("System Ready")

while True:

    # Most IR sensors:
    # 0 = Object Detected
    # 1 = No Object

    if ir.value() == 0:

        print("Object Detected")
        print("Gate Opening")

        set_angle(90)      # Open gate
        time.sleep(3)

        print("Gate Closing")

        set_angle(0)       # Close gate
        time.sleep(1)

        # Wait until object leaves
        while ir.value() == 0:
            time.sleep(0.1)

    time.sleep(0.1)