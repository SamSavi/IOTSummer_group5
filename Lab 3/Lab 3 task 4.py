import network
import time
import urequests as requests
from machine import Pin

# ---------- CONFIG ----------
WIFI_SSID = "Robotic WIFI"
WIFI_PASS = "rbtWIFI@2025"

BLYNK_TOKEN = "VwK_0kF-U--rmoyTncJ93w6DHikAUq6k"
BLYNK_API = "http://blynk.cloud/external/api"

IR_PIN = 12
TM_DIO = 16
TM_CLK = 17

BLYNK_COUNTER_PIN = "V3"

# ---------- TM1637 WITHOUT LIBRARY ----------
class TM1637:
    SEGMENTS = [
        0x3f,  # 0
        0x06,  # 1
        0x5b,  # 2
        0x4f,  # 3
        0x66,  # 4
        0x6d,  # 5
        0x7d,  # 6
        0x07,  # 7
        0x7f,  # 8
        0x6f   # 9
    ]

    def __init__(self, clk_pin, dio_pin):
        self.clk = Pin(clk_pin, Pin.OUT)
        self.dio = Pin(dio_pin, Pin.OUT)
        self.clk.value(1)
        self.dio.value(1)
        self.brightness = 7

    def start(self):
        self.dio.value(1)
        self.clk.value(1)
        time.sleep_us(5)
        self.dio.value(0)

    def stop(self):
        self.clk.value(0)
        time.sleep_us(5)
        self.dio.value(0)
        time.sleep_us(5)
        self.clk.value(1)
        time.sleep_us(5)
        self.dio.value(1)

    def write_byte(self, data):
        for i in range(8):
            self.clk.value(0)
            self.dio.value((data >> i) & 1)
            time.sleep_us(5)
            self.clk.value(1)
            time.sleep_us(5)

        self.clk.value(0)
        self.dio.value(1)
        time.sleep_us(5)
        self.clk.value(1)
        time.sleep_us(5)
        self.clk.value(0)

    def show_number(self, num):
        num = num % 10000
        text = "{:04d}".format(num)

        self.start()
        self.write_byte(0x40)
        self.stop()

        self.start()
        self.write_byte(0xC0)

        for digit in text:
            self.write_byte(self.SEGMENTS[int(digit)])

        self.stop()

        self.start()
        self.write_byte(0x88 + self.brightness)
        self.stop()

# ---------- HARDWARE ----------
ir = Pin(IR_PIN, Pin.IN)
display = TM1637(TM_CLK, TM_DIO)

counter = 0
last_ir_state = 1

# ---------- WIFI ----------
wifi = network.WLAN(network.STA_IF)
wifi.active(True)
wifi.connect(WIFI_SSID, WIFI_PASS)

print("Connecting to WiFi...")
while not wifi.isconnected():
    time.sleep(1)

print("WiFi Connected!")
print(wifi.ifconfig())

# ---------- BLYNK ----------
def send_to_blynk(value):
    try:
        url = f"{BLYNK_API}/update?token={BLYNK_TOKEN}&{BLYNK_COUNTER_PIN}={value}"
        r = requests.get(url)
        r.close()
        print("Sent to Blynk:", value)
    except Exception as e:
        print("Blynk Error:", e)

# ---------- START ----------
display.show_number(counter)
send_to_blynk(counter)

print("System Ready")

# ---------- MAIN LOOP ----------
while True:
    ir_state = ir.value()

    # Most IR sensors: 0 = detected
    if ir_state == 0 and last_ir_state == 1:
        counter += 1

        print("Object Detected! Count =", counter)

        display.show_number(counter)
        send_to_blynk(counter)

        time.sleep(0.5)

    last_ir_state = ir_state
    time.sleep(0.1)