import network, socket, utime, dht, _thread
from machine import Pin, I2C
import lcd_i2c as lcd

# --- Hardware ---
led     = Pin(2, Pin.OUT)
dht_pin = dht.DHT22(Pin(4))
trig    = Pin(27, Pin.OUT)
echo    = Pin(26, Pin.IN)
i2c     = I2C(0, sda=Pin(21), scl=Pin(22), freq=400000)
lcd.lcd_init(i2c)
lcd.lcd_clear(i2c)

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
        return round(dht_pin.temperature(), 2), round(dht_pin.humidity(), 2)
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

# --- URL decode helper ---
def url_decode(s):
    result = ""
    i = 0
    while i < len(s):
        if s[i] == '%' and i + 2 < len(s):
            result += chr(int(s[i+1:i+3], 16))
            i += 3
        elif s[i] == '+':
            result += ' '
            i += 1
        else:
            result += s[i]
            i += 1
    return result

# --- Shared LCD state ---
lcd_mode        = "auto"
lcd_custom_text = ""

# --- LCD background thread ---
def lcd_thread():
    while True:
        if lcd_mode == "auto":
            temp, hum = read_dht()
            dist      = read_distance()
            lcd.lcd_clear(i2c)
            lcd.lcd_write(i2c, f"Temp: {temp}C   ", 1)
            lcd.lcd_write(i2c, f"Dist: {dist}cm  ", 2)

        elif lcd_mode == "temp":
            temp, hum = read_dht()
            lcd.lcd_clear(i2c)
            lcd.lcd_write(i2c, f"Temp: {temp}C   ", 1)
            lcd.lcd_write(i2c, f"Hum:  {hum}%    ", 2)

        elif lcd_mode == "dist":
            dist = read_distance()
            lcd.lcd_clear(i2c)
            lcd.lcd_write(i2c, f"Dist: {dist}cm  ", 1)
            lcd.lcd_write(i2c, "                ", 2)

        elif lcd_mode == "text":
            # Stay still, don't refresh — just show the text
            lcd.lcd_clear(i2c)
            lcd.lcd_write(i2c, lcd_custom_text[:16],   1)
            lcd.lcd_write(i2c, lcd_custom_text[16:32], 2)
            utime.sleep(2)
            continue

        utime.sleep(2)

# --- HTML ---
def web_page(led_state, temp, hum, dist):
    led_color = "#4CAF50" if led_state else "#f44336"
    led_label = "ON" if led_state else "OFF"
    return f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <meta http-equiv="refresh" content="2">
  <title>ESP32 - Task 4</title>
  <style>
    body {{ font-family: Arial; text-align: center;
            background: #1e1e2e; color: #cdd6f4; padding: 30px; }}
    h1   {{ color: #cba6f7; }}
    .card {{ background: #313244; border-radius: 12px;
             padding: 25px; max-width: 380px; margin: 15px auto; }}
    .badge {{ display:inline-block; background:{led_color}; color:#fff;
              padding:5px 16px; border-radius:20px; font-weight:bold; }}
    .val  {{ font-size: 1.3em; margin: 8px 0; }}
    button {{ padding:11px 24px; margin:6px; border:none;
              border-radius:8px; font-size:0.95em; cursor:pointer; }}
    .on   {{ background:#a6e3a1; color:#1e1e2e; font-weight:bold; }}
    .off  {{ background:#f38ba8; color:#1e1e2e; font-weight:bold; }}
    .lcd  {{ background:#89b4fa; color:#1e1e2e; font-weight:bold; }}
    .auto {{ background:#cba6f7; color:#1e1e2e; font-weight:bold; }}
    .send {{ background:#f9e2af; color:#1e1e2e; font-weight:bold; }}
    input[type=text] {{ padding:9px; border-radius:6px; border:none;
                        width:210px; font-size:1em; margin:6px;
                        background:#45475a; color:#cdd6f4; }}
    .hint {{ font-size:0.78em; color:#6c7086; margin-top:4px; }}
  </style>
</head>
<body>
  <h1>🌐 ESP32 IoT - Task 4</h1>

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
    <p class="hint">Auto-refreshes every 2 seconds</p>
  </div>

  <!-- LCD Card -->
  <div class="card">
    <h2>🖥️ LCD Control</h2>
    <a href="/lcd/auto"><button class="auto">🔄 Auto (Temp+Dist)</button></a>
    <br>
    <a href="/lcd/temp"><button class="lcd">Show Temp+Humidity</button></a>
    <a href="/lcd/dist"><button class="lcd">Show Distance</button></a>
    <br><br>
    <hr style="border-color:#45475a;">
    <p style="margin:10px 0 6px;"><b>✏️ Custom Message</b></p>
    <form action="/lcd/text" method="get">
      <input type="text" name="msg" placeholder="Type message..." maxlength="32">
      <br>
      <button type="submit" class="send">📨 Send to LCD</button>
    </form>
    <p class="hint">Max 32 chars — wraps to line 2 after 16</p>
  </div>

</body>
</html>"""

# --- Server ---
def run_server(ip):
    global lcd_mode, lcd_custom_text

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

        # Read sensors
        temp, hum = read_dht()
        dist      = read_distance()

        # LED routes
        if path == '/led/on':
            led.on();  led_state = True
            print("LED → ON")
        elif path == '/led/off':
            led.off(); led_state = False
            print("LED → OFF")

        # LCD mode routes
        elif path == '/lcd/auto':
            lcd_mode = "auto"
            print("LCD → Auto mode")
        elif path == '/lcd/temp':
            lcd_mode = "temp"
            print("LCD → Temp mode")
        elif path == '/lcd/dist':
            lcd_mode = "dist"
            print("LCD → Distance mode")

        # Textbox → LCD
        elif '/lcd/text' in path:
            msg = ""
            if 'msg=' in path:
                raw = path.split('msg=')[1].split('&')[0]
                msg = url_decode(raw)
            lcd_custom_text = msg
            lcd_mode        = "text"
            print(f"LCD → Text: {msg}")

        html = web_page(led_state, temp, hum, dist)
        conn.send("HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n")
        conn.send(html)
        conn.close()

# --- Run ---
ip = connect_wifi()
lcd.lcd_clear(i2c)
lcd.lcd_write(i2c, "Server Ready", 1)
lcd.lcd_write(i2c, ip, 2)
utime.sleep(2)

_thread.start_new_thread(lcd_thread, ())
run_server(ip)