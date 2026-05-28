from machine import Pin
import dht
import network
import urequests
import time

# ── Configuration ────────────────────────────────────────────────
SSID = "Robotic WIFI"
PASSWORD = "rbtWIFI@2025"

BOT_TOKEN = "8961773441:AAFS-YSGBIzuKoczxh430u955JYLHs3XnMQ"
CHAT_ID = "-1003723087696"

# ── Hardware Setup ───────────────────────────────────────────────
sensor = dht.DHT22(Pin(16))     # DHT22 data pin → GPIO 16

relay       = Pin(25, Pin.OUT)  # Relay control pin → GPIO 25
relay.value(0)                  # Start OFF

# ── State ────────────────────────────────────────────────────────
relay_state    = False
last_update_id = 0

# ════════════════════════════════════════════════════════════════
# Wi-Fi Connect
# ════════════════════════════════════════════════════════════════
def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if wlan.isconnected():
        return
    print("Connecting to Wi-Fi...")
    wlan.connect(WIFI_SSID, WIFI_PASSWORD)
    for _ in range(20):
        if wlan.isconnected():
            print("Connected! IP:", wlan.ifconfig()[0])
            return
        time.sleep(0.5)
    print("Wi-Fi failed!")

# ════════════════════════════════════════════════════════════════
# Telegram — Send Message
# ════════════════════════════════════════════════════════════════
def send_message(text):
    url = "https://api.telegram.org/bot{}/sendMessage".format(BOT_TOKEN)
    payload = {
        "chat_id": CHAT_ID,
        "text":    text
    }
    try:
        response = urequests.post(url, json=payload)
        if response.status_code == 200:
            print("Message sent!")
        else:
            print("Telegram error:", response.status_code)
        response.close()
    except Exception as e:
        print("Send failed:", e)

# ════════════════════════════════════════════════════════════════
# Telegram — Get Updates & Handle Commands
# ════════════════════════════════════════════════════════════════
def get_updates():
    global last_update_id
    url = "https://api.telegram.org/bot{}/getUpdates?offset={}&timeout=1".format(
        BOT_TOKEN, last_update_id + 1
    )
    try:
        response = urequests.get(url)
        if response.status_code != 200:
            print("getUpdates error:", response.status_code)
            response.close()
            return []
        data = response.json()
        response.close()
        return data.get("result", [])
    except Exception as e:
        print("getUpdates failed:", e)
        return []


def handle_commands(temperature, humidity):
    global relay_state, last_update_id

    updates = get_updates()

    for update in updates:
        last_update_id = update["update_id"]

        msg  = update.get("message", {})
        text = msg.get("text", "").strip().lower()

        print("Command received:", text)

        # ── /status ──────────────────────────────────────────
        if text == "/status":
            relay_label = "ON" if relay_state else "OFF"
            reply = (
                "Temp:     {:.2f} C\n"
                "Humidity: {:.2f} %\n"
                "Light:    {}"
            ).format(temperature, humidity, relay_label)
            send_message(reply)

        # ── /on ──────────────────────────────────────────────
        elif text == "/on":
            relay.value(1)
            relay_state = True
            send_message("Light turned ON.")

        # ── /off ─────────────────────────────────────────────
        elif text == "/off":
            relay.value(0)
            relay_state = False
            send_message("Light turned OFF.")

# ── Main ─────────────────────────────────────────────────────────
connect_wifi()
send_message("ESP32 online! Try /status /on /off")

print("DHT22 Sensor Reading Started...")
print("---------------------------")

while True:
    try:
        sensor.measure()

        temperature = sensor.temperature()   # °C
        humidity    = sensor.humidity()       # %

        print("Temperature: {:.2f} °C".format(temperature))
        print("Humidity:    {:.2f} %".format(humidity))
        print("---------------------------")

        handle_commands(temperature, humidity)

    except OSError:
        print("Failed to read from DHT22 sensor")

    time.sleep(5)