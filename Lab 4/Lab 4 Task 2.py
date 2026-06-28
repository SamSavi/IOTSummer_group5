import network
import urequests
import time
from machine import Pin, ADC
from collections import deque

# WiFi
SSID = "Robotic WIFI"
PASSWORD = "rbtWIFI@2025"

# Node-RED URL
NODE_RED_URL = "http://10.30.0.215:1880/gas-data"

# Connect WiFi
wifi = network.WLAN(network.STA_IF)
wifi.active(True)
wifi.connect(SSID, PASSWORD)

print("Connecting to WiFi...")
while not wifi.isconnected():
    time.sleep(1)

print("Connected:", wifi.ifconfig())

# MQ-5 Sensor
mq5 = ADC(Pin(33))
mq5.atten(ADC.ATTN_11DB)
mq5.width(ADC.WIDTH_12BIT)

samples = deque([], 5)

while True:
    raw_value = mq5.read()

    samples.append(raw_value)
    avg_value = sum(samples) / len(samples)

    # Task 2: Gas risk classification
    if avg_value < 2100:
        risk_level = "SAFE"
    elif avg_value < 2599:
        risk_level = "WARNING"
    else:
        risk_level = "DANGER"

    print("--------------------")
    print("Raw:", raw_value)
    print("Average:", round(avg_value, 2))
    print("Risk Level:", risk_level)

    data = {
        "gas_avg": round(avg_value, 2),
        "risk_level": risk_level
    }

    try:
        response = urequests.post(NODE_RED_URL, json=data)
        print("Sent:", response.status_code)
        response.close()
    except Exception as e:
        print("Error:", e)

    time.sleep(2)