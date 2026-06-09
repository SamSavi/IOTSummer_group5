import network
import time
import urequests as requests
from machine import Pin

# ==========================
# WiFi Settings
# ==========================
WIFI_SSID = "Robotic WIFI"
WIFI_PASSWORD = "rbtWIFI@2025"

# ==========================
# Blynk Settings
# ==========================
BLYNK_TOKEN = "VwK_0kF-U--rmoyTncJ93w6DHikAUq6k"
BLYNK_API = "http://blynk.cloud/external/api"

# ==========================
# IR Sensor
# ==========================
IR = Pin(12, Pin.IN)

# ==========================
# Connect WiFi
# ==========================
wifi = network.WLAN(network.STA_IF)
wifi.active(True)

if not wifi.isconnected():
    print("Connecting to WiFi...")
    wifi.connect(WIFI_SSID, WIFI_PASSWORD)

    timeout = 15
    while not wifi.isconnected() and timeout > 0:
        time.sleep(1)
        timeout -= 1

if wifi.isconnected():
    print("WiFi Connected")
    print("IP:", wifi.ifconfig()[0])
else:
    print("WiFi Failed")
    raise SystemExit

# ==========================
# Main Loop
# ==========================
while True:

    sensor_value = IR.value()

    # Most IR obstacle sensors:
    # 0 = Object detected
    # 1 = No object

    if sensor_value == 0:
        print("Detected")
        blynk_value = 1
    else:
        print("Not Detected")
        blynk_value = 0

    try:
        url = f"{BLYNK_API}/update?token={BLYNK_TOKEN}&V2={blynk_value}"

        response = requests.get(url)

        print("Blynk:", response.text)

        response.close()

    except Exception as e:
        print("Blynk Error:", e)

    time.sleep(1)