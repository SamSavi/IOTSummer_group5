import network
import time
import json
from machine import Pin, ADC, I2C
from collections import deque
from umqtt.simple import MQTTClient
from bmp280 import BMP280
from ds3231 import DS3231
from mlx90614 import MLX90614

# ---------- WiFi ----------
SSID = "Robotic WIFI"
PASSWORD = "rbtWIFI@2025"

# ---------- MQTT ----------
MQTT_BROKER = "test.mosquitto.org"
MQTT_PORT = 1883
MQTT_TOPIC = b"/aupp/esp32/bmp280/Group5"
CLIENT_ID = b"esp32_group5_task4"

# ---------- Connect WiFi ----------
wifi = network.WLAN(network.STA_IF)
wifi.active(True)
wifi.connect(SSID, PASSWORD)

print("Connecting to WiFi...")
while not wifi.isconnected():
    time.sleep(1)

print("WiFi connected:", wifi.ifconfig())

# ---------- Connect MQTT ----------
client = MQTTClient(CLIENT_ID, MQTT_BROKER, port=MQTT_PORT)
client.connect()
print("Connected to MQTT broker")

# ---------- MQ-5 ----------
mq5 = ADC(Pin(33))
mq5.atten(ADC.ATTN_11DB)
mq5.width(ADC.WIDTH_12BIT)

gas_samples = deque([], 5)

# ---------- I2C ----------
i2c = I2C(0, scl=Pin(22), sda=Pin(21), freq=100000)
print("I2C devices:", i2c.scan())

bmp = BMP280(i2c)
rtc = DS3231(i2c)
mlx = MLX90614(i2c)

while True:
    # Gas average
    gas_raw = mq5.read()
    gas_samples.append(gas_raw)
    gas_avg = sum(gas_samples) / len(gas_samples)

    # Risk level
    if gas_avg < 2100:
        risk_level = "SAFE"
    elif gas_avg < 2600:
        risk_level = "WARNING"
    else:
        risk_level = "DANGER"

    # Body temp
    body_temp = mlx.read_object_temp()

    # Fever flag
    if body_temp >= 32.5:
        fever_flag = 1
    else:
        fever_flag = 0

    # BMP280
    pressure = bmp.pressure / 100
    altitude = bmp.altitude

    # DS3231
    t = rtc.get_time()
    timestamp = "{:04d}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}".format(
        t[0], t[1], t[2], t[3], t[4], t[5]
    )

    data = {
        "gas_avg": round(gas_avg, 2),
        "risk_level": risk_level,
        "body_temp": round(body_temp, 2),
        "fever_flag": fever_flag,
        "pressure": round(pressure, 2),
        "altitude": round(altitude, 2),
        "timestamp": timestamp
    }

    msg = json.dumps(data)

    print("--------------------")
    print(msg)

    client.publish(MQTT_TOPIC, msg)

    time.sleep(2)