import network, socket, utime
from machine import Pin

# --- Hardware ---
led = Pin(2, Pin.OUT)

# --- Wi-Fi ---
SSID = "Robotic WIFI"
PASSWORD = "rbtWIFI@2025"

def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(False)      # ← reset first
    utime.sleep(0.5)
    wlan.active(True)       # ← then turn back on
    wlan.connect(SSID, PASSWORD)
    print("Connecting", end="")
    while not wlan.isconnected():
        print(".", end="")
        utime.sleep(0.5)
    print("\nConnected:", wlan.ifconfig()[0])
    return wlan.ifconfig()[0]

# --- HTML ---
def web_page(led_state):
    color = "#4CAF50" if led_state else "#f44336"
    label = "ON" if led_state else "OFF"
    return f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>LED Control</title>
  <style>
    body {{ font-family: Arial; text-align: center; background: #1e1e2e; color: #cdd6f4; padding: 40px; }}
    h1 {{ color: #cba6f7; }}
    .card {{ background: #313244; border-radius: 12px; padding: 30px; max-width: 360px; margin: auto; }}
    .badge {{ display:inline-block; background:{color}; color:#fff;
              padding:6px 18px; border-radius:20px; font-weight:bold; font-size:1.1em; }}
    button {{ padding: 12px 30px; margin: 10px; border: none;
              border-radius: 8px; font-size: 1em; cursor: pointer; }}
    .on  {{ background: #a6e3a1; color: #1e1e2e; font-weight: bold; }}
    .off {{ background: #f38ba8; color: #1e1e2e; font-weight: bold; }}
  </style>
</head>
<body>
  <h1>💡 LED Control</h1>
  <div class="card">
    <p>LED is currently: <span class="badge">{label}</span></p>
    <br>
    <a href="/led/on" ><button class="on" >Turn ON</button></a>
    <a href="/led/off"><button class="off">Turn OFF</button></a>
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

        if path == '/led/on':
            led.on()
            led_state = True
            print("LED → ON")
        elif path == '/led/off':
            led.off()
            led_state = False
            print("LED → OFF")

        html = web_page(led_state)
        conn.send("HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n")
        conn.send(html)
        conn.close()

# --- Run ---
ip = connect_wifi()
run_server(ip)