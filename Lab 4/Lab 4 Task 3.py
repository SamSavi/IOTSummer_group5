import network
import urequests
import time
from machine import Pin, I2C
from mlx90614 import MLX90614

# ---------- WiFi ----------
SSID = "Robotic WIFI"
PASSWORD = "rbtWIFI@2025"

# ---------- Node-RED ----------
NODE_RED_URL = "http://10.30.0.215:1880/gas-data"

# ---------- Connect WiFi ----------
wifi = network.WLAN(network.STA_IF)
wifi.active(True)
wifi.connect(SSID, PASSWORD)

print("Connecting to WiFi...")
while not wifi.isconnected():
    time.sleep(1)

print("Connected:", wifi.ifconfig())

# ---------- MLX90614 ----------
i2c = I2C(0, scl=Pin(22), sda=Pin(21), freq=100000)

print("I2C devices found:", i2c.scan())

mlx = MLX90614(i2c)

while True:

    body_temp = mlx.read_object_temp()

    if body_temp >= 32.5:
        fever_flag = 1
    else:
        fever_flag = 0

    print("--------------------")
    print("Body Temp:", round(body_temp, 2))
    print("Fever Flag:", fever_flag)

    data = {
        "body_temp": round(body_temp, 2),
        "fever_flag": fever_flag
    }

    try:
        response = urequests.post(NODE_RED_URL, json=data)
        print("Sent:", response.status_code)
        response.close()

    except Exception as e:
        print("Error:", e)

    time.sleep(2)