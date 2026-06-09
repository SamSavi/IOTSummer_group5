import network
import time
import urequests as requests
from machine import Pin, PWM

# ==========================
# WiFi
# ==========================
WIFI_SSID = "Robotic WIFI"
WIFI_PASSWORD = "rbtWIFI@2025"

# ==========================
# Blynk Settings
# ==========================
BLYNK_TOKEN = "VwK_0kF-U--rmoyTncJ93w6DHikAUq6k"
BLYNK_API = "http://blynk.cloud/external/api"

# ==========================
# Servo on GPIO 13
# ==========================
servo = PWM(Pin(13), freq=50)

def set_angle(angle):
    # Convert 0-180 degrees to PWM duty
    duty = int((angle / 180) * 102 + 26)
    servo.duty(duty)

# ==========================
# Connect WiFi
# ==========================
wifi = network.WLAN(network.STA_IF)
wifi.active(True)

if not wifi.isconnected():
    print("Connecting WiFi...")
    wifi.connect(WIFI_SSID, WIFI_PASSWORD)

    while not wifi.isconnected():
        time.sleep(1)

print("WiFi Connected")
print("IP:", wifi.ifconfig()[0])

# ==========================
# Main Loop
# ==========================
while True:

    try:
        url = f"{BLYNK_API}/get?token={BLYNK_TOKEN}&V4"

        response = requests.get(url)

        angle = int(response.text)

        response.close()

        if angle < 0:
            angle = 0
        elif angle > 180:
            angle = 180

        set_angle(angle)

        print("Servo Angle:", angle)

    except Exception as e:
        print("Error:", e)

    time.sleep(0.5)