import network
import time
import urequests as requests
from machine import Pin, PWM

# ---------- CONFIG ----------
WIFI_SSID = "Robotic WIFI"
WIFI_PASS = "rbtWIFI@2025"

BLYNK_TOKEN = "VwK_0kF-U--rmoyTncJ93w6DHikAUq6k"
BLYNK_API = "http://blynk.cloud/external/api"

IR_PIN = 12
SERVO_PIN = 13
TM_DIO = 16
TM_CLK = 17

V_COUNTER = "V3"
V_AUTO = "V5"

# ---------- TM1637 WITHOUT LIBRARY ----------
class TM1637:
    SEGMENTS = [0x3f, 0x06, 0x5b, 0x4f, 0x66,
                0x6d, 0x7d, 0x07, 0x7f, 0x6f]

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

servo = PWM(Pin(SERVO_PIN), freq=50)

# ---------- SERVO ----------
def servo_angle(angle):
    duty = int(26 + (angle / 180) * 102)
    servo.duty(duty)

def open_gate():
    servo_angle(90)

def close_gate():
    servo_angle(0)

# ---------- BLYNK ----------
def blynk_update(pin, value):
    try:
        url = f"{BLYNK_API}/update?token={BLYNK_TOKEN}&{pin}={value}"
        r = requests.get(url)
        r.close()
    except Exception as e:
        print("Blynk Update Error:", e)

def blynk_get(pin):
    try:
        url = f"{BLYNK_API}/get?token={BLYNK_TOKEN}&{pin}"
        r = requests.get(url)
        value = r.text
        r.close()
        return int(value.strip('["]'))
    except Exception as e:
        print("Blynk Get Error:", e)
        return 1

# ---------- VARIABLES ----------
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

# ---------- START ----------
close_gate()
display.show_number(counter)
blynk_update(V_COUNTER, counter)

print("System Ready")
print("V5 = 1 Auto Mode, V5 = 0 Manual Mode")

# ---------- MAIN LOOP ----------
while True:
    auto_mode = blynk_get(V_AUTO)

    if auto_mode == 1:
        ir_state = ir.value()

        if ir_state == 0 and last_ir_state == 1:
            counter += 1

            print("Auto Mode: Object Detected! Count =", counter)

            display.show_number(counter)
            blynk_update(V_COUNTER, counter)

            open_gate()
            time.sleep(2)
            close_gate()

        last_ir_state = ir_state

    else:
        print("Manual Mode: IR Ignored")
        time.sleep(0.5)

    time.sleep(0.1)