import network, socket, utime, dht
from machine import Pin

# --- Hardware ---
led     = Pin(2, Pin.OUT)
dht_pin = dht.DHT22(Pin(4))
trig    = Pin(27, Pin.OUT)
echo    = Pin(26, Pin.IN)

# --- Wi-Fi ---
SSID = "Robotic WIFI"
PASSWORD = "rbtWIFI@2025"

def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(False)
    utime.sleep(0.5)
    wlan.active(True)
    wlan.connect(SSID, PASSWORD)
    print("Connecting", end="")
    while not wlan.isconnected():
        print(".", end="")
        utime.sleep(0.5)
    print("\nConnected:", wlan.ifconfig()[0])
    return wlan.ifconfig()[0]

# --- Sensors ---
def read_dht():
    try:
        dht_pin.measure()
        utime.sleep_ms(500)
        return dht_pin.temperature(), dht_pin.humidity()
    except:
        return "--", "--"

def read_distance():
    try:
        trig.off()
        utime.sleep_us(2)
        trig.on()
        utime.sleep_us(10)
        trig.off()

        timeout = utime.ticks_us() + 30000
        while echo.value() == 0:
            if utime.ticks_us() > timeout:
                return "--"
        t1 = utime.ticks_us()

        timeout = utime.ticks_us() + 30000
        while echo.value() == 1:
            if utime.ticks_us() > timeout:
                return "--"
        t2 = utime.ticks_us()

        return round((t2 - t1) * 0.0343 / 2, 1)
    except:
        return "--"

# --- HTML ---
def web_page(led_state, temp, hum, dist):
    led_color = "#4CAF50" if led_state else "#f44336"
    led_label = "ON" if led_state else "OFF"
    return f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <meta http-equiv="refresh" content="2">
  <title>ESP32 - Task 2</title>
  <style>
    body {{ font-family: Arial; text-align: center;
            background: #1e1e2e; color: #cdd6f4; padding: 40px; }}
    h1   {{ color: #cba6f7; }}
    .card {{ background: #313244; border-radius: 12px;
             padding: 25px; max-width: 380px; margin: 15px auto; }}
    .badge {{ display:inline-block; background:{led_color}; color:#fff;
              padding:5px 16px; border-radius:20px; font-weight:bold; }}
    .val  {{ font-size: 1.4em; margin: 10px 0; }}
    button {{ padding:11px 28px; margin:8px; border:none;
              border-radius:8px; font-size:1em; cursor:pointer; }}
    .on  {{ background:#a6e3a1; color:#1e1e2e; font-weight:bold; }}
    .off {{ background:#f38ba8; color:#1e1e2e; font-weight:bold; }}
  </style>
</head>
<body>
  <h1>🌐 ESP32 IoT - Task 2</h1>

  <!-- LED Card -->
  <div class="card">
    <h2>💡 LED &nbsp;<span class="badge">{led_label}</span></h2>
    <a href="/led/on" ><button class="on" >Turn ON</button></a>
    <a href="/led/off"><button class="off">Turn OFF</button></a>
  </div>

  <!-- Sensor Card -->
  <div class="card">
    <h2>📊 Sensor Readings</h2>
    <p class="val">🌡️ Temperature : <b>{temp} °C</b></p>
    <p class="val">💧 Humidity    : <b>{hum} %</b></p>
    <p class="val">📏 Distance    : <b>{dist} cm</b></p>
    <p style="font-size:0.8em; color:#6c7086;">Auto-refreshes every 2 seconds</p>
  </div>
</body>
</html>"""

# --- Server ---
def run_server(ip):
    s = socket.socket()
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(('', 80))
    s.listen(5)
    print(f"Open browser → http://{ip}/")

    led_state = False

    while True:
        conn, addr = s.accept()
        request = conn.recv(512).decode()
        path = request.split(' ')[1] if ' ' in request else '/'

        # LED routes
        if path == '/led/on':
            led.on()
            led_state = True
            print("LED → ON")
        elif path == '/led/off':
            led.off()
            led_state = False
            print("LED → OFF")

        # Read sensors on every page load
        temp, hum = read_dht()
        dist      = read_distance()

        html = web_page(led_state, temp, hum, dist)
        conn.send("HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n")
        conn.send(html)
        conn.close()

# --- Run ---
ip = connect_wifi()
run_server(ip)