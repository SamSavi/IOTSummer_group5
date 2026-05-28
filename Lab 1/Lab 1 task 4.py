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

TEMP_THRESHOLD = 34.0            # °C — alert above this

# ── Hardware Setup ───────────────────────────────────────────────
sensor = dht.DHT22(Pin(16))      # DHT22 data pin → GPIO 16

relay       = Pin(25, Pin.OUT)   # Light control pin → GPIO 25
relay.value(0)                   # Start OFF

# ── State ────────────────────────────────────────────────────────
relay_state    = False           # True = Light ON
alert_active   = False           # True = we are in alert loop
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
    global relay_state, alert_active, last_update_id

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
            relay_state  = True
            alert_active = False        # Stop alert loop
            send_message("Light turned ON. Alert stopped.")

        # ── /off ─────────────────────────────────────────────
        elif text == "/off":
            relay.value(0)
            relay_state  = False
            alert_active = False
            send_message("Light turned OFF.")

# ════════════════════════════════════════════════════════════════
# TASK 4 — Alert Logic & Auto-OFF
# ════════════════════════════════════════════════════════════════
def handle_alert_logic(temperature):
    global relay_state, alert_active

    # ── Temp HIGH ────────────────────────────────────────────
    if temperature >= TEMP_THRESHOLD:
        if not relay_state:
            # Light is still OFF → keep sending alert every 5s
            alert_active = True
            send_message(
                "ALERT: Temp is {:.2f} C\n"
                "Above {} C threshold!\n"
                "Send /on to turn light ON.".format(temperature, TEMP_THRESHOLD)
            )
        # If light is already ON (user sent /on) → do nothing, no more alerts

    # ── Temp LOW ─────────────────────────────────────────────
    else:
        if relay_state:
            # Temp dropped below threshold → auto turn OFF light
            relay.value(0)
            relay_state  = False
            alert_active = False
            send_message(
                "Temp dropped to {:.2f} C\n"
                "Below {} C. Light auto-OFF.".format(temperature, TEMP_THRESHOLD)
            )
        # If light already OFF and temp is fine → stay silent

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
        print("Threshold:   {:.2f} °C".format(TEMP_THRESHOLD))
        print("Light:       {}".format("ON" if relay_state else "OFF"))
        print("---------------------------")

        # Check commands first, then alert logic
        handle_commands(temperature, humidity)
        handle_alert_logic(temperature)

    except OSError:
        print("Failed to read from DHT22 sensor")

    time.sleep(5)