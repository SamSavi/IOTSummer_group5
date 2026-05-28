import network
import urequests
import time
from machine import Pin

# -------- SETTINGS --------
SSID = "Robotic WIFI"
PASSWORD = "rbtWIFI@2025"

BOT_TOKEN = "8961773441:AAFS-YSGBIzuKoczxh430u955JYLHs3XnMQ"
CHAT_ID = "-1003723087696"

# -------- LED --------
led = Pin(25, Pin.OUT)
led.value(0)

# -------- WIFI --------
wifi = network.WLAN(network.STA_IF)
wifi.active(False)      # ← Add this: reset first
time.sleep(1)           # ← Small delay
wifi.active(True)
wifi.disconnect()       # ← Add this: clear old state
time.sleep(1)           # ← Small delay
wifi.connect(SSID, PASSWORD)

while not wifi.isconnected():
    time.sleep(1)

print("WiFi connected")

# -------- TELEGRAM --------
URL = "https://api.telegram.org/bot{}/getUpdates".format(BOT_TOKEN)
last_id = 0

# -------- MAIN LOOP --------
while True:
    try:
        r = urequests.get(URL + "?offset={}".format(last_id + 1))
        messages = r.json()["result"]
        r.close()

        for msg in messages:
            last_id = msg["update_id"]
            text = msg["message"]["text"]
            chat_id = msg["message"]["chat"]["id"]

            print("Recived massage:", text)

    except:
        pass

    time.sleep(1)
