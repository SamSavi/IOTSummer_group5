import network
import time
import urequests
from machine import Pin, ADC, I2C
from collections import deque
from bmp280 import BMP280

# ==========================================
# Wi-Fi Configuration
# ==========================================
SSID = "Robotic WIFI"
PASSWORD = "rbtWIFI@2025"

# ==========================================
# Node-RED
# ==========================================
NODE_RED_URL = "http://10.30.0.215:1880/gas-data"

# ==========================================
# Telegram
# ==========================================
BOT_TOKEN = "8601033528:AAFfXvvWxQFrWPlLl_d0NMo9t3_Ya9-f3Kc"
CHAT_ID = "-5294824506"

# ==========================================
# Camera and Grafana Links
# ==========================================
CAMERA_URL = "http://10.30.0.170/"
CAMERA_STREAM_URL =     
GRAFANA_URL = "http://10.30.0.215:3000/"

# ==========================================
# ESP32 Pins
# ==========================================
MQ5_PIN = 33
BUZZER_PIN = 25

SDA_PIN = 21
SCL_PIN = 22

# ==========================================
# Gas Thresholds
# ==========================================
SAFE_LIMIT = 2100
DANGER_LIMIT = 2600

# Prevent repeated Telegram messages
telegram_alert_sent = False


# ==========================================
# Wi-Fi Connection
# ==========================================
def connect_wifi():
    wifi = network.WLAN(network.STA_IF)
    wifi.active(True)

    if not wifi.isconnected():
        print("Connecting to Wi-Fi...")
        wifi.connect(SSID, PASSWORD)

        timeout = 30

        while not wifi.isconnected() and timeout > 0:
            print(".", end="")
            time.sleep(1)
            timeout -= 1

    if wifi.isconnected():
        print()
        print("================================")
        print("Wi-Fi connected")
        print("ESP32 IP:", wifi.ifconfig()[0])
        print("================================")
    else:
        print()
        print("Wi-Fi connection failed")

    return wifi


# ==========================================
# Telegram Message Function
# ==========================================
def send_telegram_message(message):
    if BOT_TOKEN == "PASTE_YOUR_NEW_BOT_TOKEN_HERE":
        print("Telegram token has not been added")
        return False

    response = None

    try:
        telegram_url = (
            "https://api.telegram.org/bot"
            + BOT_TOKEN
            + "/sendMessage"
        )

        payload = {
            "chat_id": CHAT_ID,
            "text": message,
            "disable_web_page_preview": False
        }

        response = urequests.post(
            telegram_url,
            json=payload
        )

        print("Telegram status:", response.status_code)

        if response.status_code == 200:
            print("Telegram alert sent")
            return True

        print("Telegram response:", response.text)
        return False

    except Exception as error:
        print("Telegram error:", error)
        return False

    finally:
        if response is not None:
            response.close()


# ==========================================
# Send Data to Node-RED
# ==========================================
def send_to_node_red(data):
    response = None

    try:
        response = urequests.post(
            NODE_RED_URL,
            json=data
        )

        print("Node-RED status:", response.status_code)

    except Exception as error:
        print("Node-RED error:", error)

    finally:
        if response is not None:
            response.close()


# ==========================================
# Connect to Wi-Fi
# ==========================================
wifi = connect_wifi()

# ==========================================
# MQ-5 Gas Sensor
# ==========================================
mq5 = ADC(Pin(MQ5_PIN))
mq5.atten(ADC.ATTN_11DB)
mq5.width(ADC.WIDTH_12BIT)

gas_samples = deque([], 5)

# ==========================================
# TMB12A05 Active Buzzer
# ==========================================
buzzer = Pin(BUZZER_PIN, Pin.OUT)
buzzer.value(0)
# ==========================================
# BMP280
# ==========================================
i2c = I2C(
    0,
    scl=Pin(SCL_PIN),
    sda=Pin(SDA_PIN),
    freq=100000
)

devices = i2c.scan()

print("I2C devices:", devices)

if 118 not in devices:
    raise OSError(
        "BMP280 not found. Expected address 118 (0x76)"
    )

bmp = BMP280(i2c, addr=0x76)

# Give the sensor time to stabilize
time.sleep(2)

# ==========================================
# Main Loop
# ==========================================
while True:
    try:
        # Reconnect Wi-Fi if disconnected
        if not wifi.isconnected():
            wifi = connect_wifi()

        # ----------------------------------
        # Read MQ-5
        # ----------------------------------
        gas_raw = mq5.read()

        gas_samples.append(gas_raw)

        gas_avg = (
            sum(gas_samples)
            / len(gas_samples)
        )

        # ----------------------------------
        # Classify Gas Risk
        # ----------------------------------
        if gas_avg < SAFE_LIMIT:
            risk_level = "SAFE"

        elif gas_avg < DANGER_LIMIT:
            risk_level = "WARNING"

        else:
            risk_level = "DANGER"

        # ----------------------------------
        # Read BMP280
        # ----------------------------------
        temperature = bmp.temperature
        pressure = bmp.pressure / 100
        altitude = bmp.altitude

        # ----------------------------------
        # Alarm and Telegram Logic
        # ----------------------------------
        if risk_level == "DANGER":
            buzzer.value(1)
            alarm = 1

            if not telegram_alert_sent:
                message = (
                    "GAS DANGER DETECTED!\n\n"
                    "Gas Raw: {}\n"
                    "Gas Average: {}\n"
                    "Status: {}\n"
                    "Temperature: {} C\n"
                    "Pressure: {} hPa\n"
                    "Altitude: {} m\n\n"
                    "Live Camera:\n{}\n\n"
                    "Direct Camera Stream:\n{}\n\n"
                    "Grafana Dashboard:\n{}"
                ).format(
                    gas_raw,
                    round(gas_avg, 2),
                    risk_level,
                    round(temperature, 2),
                    round(pressure, 2),
                    round(altitude, 2),
                    CAMERA_URL,
                    CAMERA_STREAM_URL,
                    GRAFANA_URL
                )

                sent = send_telegram_message(message)

                if sent:
                    telegram_alert_sent = True

        else:
            buzzer.value(0)
            alarm = 0

            # Allow a new Telegram alert after danger clears
            telegram_alert_sent = False

        # ----------------------------------
        # JSON Packet for Node-RED
        # ----------------------------------
        data = {
            "gas_raw": gas_raw,
            "gas_avg": round(gas_avg, 2),
            "risk_level": risk_level,
            "temperature": round(temperature, 2),
            "pressure": round(pressure, 2),
            "altitude": round(altitude, 2),
            "alarm": alarm,
            "camera_url": CAMERA_URL,
            "camera_stream_url": CAMERA_STREAM_URL,
            "grafana_url": GRAFANA_URL
        }

        # ----------------------------------
        # Serial Monitor
        # ----------------------------------
        print("--------------------------------")
        print("Gas Raw       :", gas_raw)
        print("Gas Average   :", round(gas_avg, 2))
        print("Risk Level    :", risk_level)
        print("Temperature   :", round(temperature, 2), "C")
        print("Pressure      :", round(pressure, 2), "hPa")
        print("Altitude      :", round(altitude, 2), "m")
        print("Alarm         :", alarm)
        print("Camera        :", CAMERA_URL)
        print("Grafana       :", GRAFANA_URL)
        # ----------------------------------
        # Send to Node-RED
        # ----------------------------------
        send_to_node_red(data)

    except Exception as error:
        buzzer.value(0)
        print("Main loop error:", error)

    time.sleep(2)