from machine import Pin, SPI, SoftSPI, RTC
import mfrc522
import sdcard
import os
import network
import urequests
import ujson
import ntptime
import time

# ============================================================
# WiFi Connection
# ============================================================
SSID = "Robotic WIFI"
PASSWORD = "rbtWIFI@2025"

def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print("Connecting WiFi", end="")
        wlan.connect(SSID, PASSWORD)
        timeout = 20
        while not wlan.isconnected() and timeout > 0:
            print(".", end="")
            time.sleep(0.5)
            timeout -= 1
    if wlan.isconnected():
        print("\nConnected:", wlan.ifconfig())
        return True
    else:
        print("\nWiFi connection failed")
        return False

# ============================================================
# Time Sync
# ============================================================
def sync_time():
    try:
        ntptime.settime()
        print("Time synced via NTP")
    except Exception as e:
        print("NTP sync failed:", e)
        rtc = RTC()
        rtc.datetime((2026, 7, 2, 4, 12, 0, 0, 0))

def get_datetime_str():
    offset_seconds = 7 * 3600  # Cambodia UTC+7
    t = time.localtime(time.time() + offset_seconds)
    return "{:04d}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}".format(
        t[0], t[1], t[2], t[3], t[4], t[5]
    )

# ============================================================
# Firestore Setup (no API key needed - test mode rules)
# ============================================================
PROJECT_ID = "rfid-4660c"
FIRESTORE_URL = "https://firestore.googleapis.com/v1/projects/{}/databases/(default)/documents/rfid_logs".format(PROJECT_ID)

def send_to_firestore(uid_str, student, datetime_str):
    data = {
        "fields": {
            "UID": {"stringValue": uid_str},
            "Name": {"stringValue": student["name"]},
            "StudentID": {"stringValue": student["studentID"]},
            "Major": {"stringValue": student["major"]},
            "DateTime": {"stringValue": datetime_str}
        }
    }
    try:
        res = urequests.post(FIRESTORE_URL, json=data)
        print("Sent to Firestore:", res.status_code)
        res.close()
        return True
    except Exception as e:
        print("Firestore send failed:", e)
        return False

# ============================================================
# RFID Setup
# ============================================================
rfid_sck = Pin(18, Pin.OUT)
rfid_mosi = Pin(23, Pin.OUT)
rfid_miso = Pin(19, Pin.IN)
rfid_spi = SoftSPI(baudrate=100000, polarity=0, phase=0,
                    sck=rfid_sck, mosi=rfid_mosi, miso=rfid_miso)

rst_pin = Pin(22, Pin.OUT)
cs_pin = Pin(16, Pin.OUT)
rdr = mfrc522.MFRC522(spi=rfid_spi, gpioRst=rst_pin, gpioCs=cs_pin)

# ============================================================
# SD Card Setup
# ============================================================
sd_spi = SPI(1, baudrate=1320000, polarity=0, phase=0,
             sck=Pin(14), mosi=Pin(15), miso=Pin(2))
sd_cs = Pin(13)

def init_sd():
    try:
        sd = sdcard.SDCard(sd_spi, sd_cs)
        os.mount(sd, "/sd")
        print("SD card mounted")
        try:
            os.stat("/sd/attendance.csv")
        except OSError:
            with open("/sd/attendance.csv", "w") as f:
                f.write("UID,Name,StudentID,Major,DateTime\n")
            print("Created attendance.csv with header")
        return True
    except OSError as e:
        print("SD card init failed:", e)
        return False

def save_to_sd(uid_str, student, datetime_str):
    try:
        with open("/sd/attendance.csv", "a") as f:
            f.write("{},{},{},{},{}\n".format(
                uid_str, student["name"], student["studentID"],
                student["major"], datetime_str
            ))
        print("Saved to SD card")
        return True
    except OSError as e:
        print("SD write failed:", e)
        return False

# ============================================================
# Buzzer Setup
# ============================================================
buzzer = Pin(4, Pin.OUT)

def buzz(duration_sec):
    buzzer.value(1)
    time.sleep(duration_sec)
    buzzer.value(0)

# ============================================================
# Student Database
# ============================================================
students = {
    "82-9B-37-06-28": {
        "name": "Kiari",
        "studentID": "911676767",
        "major": "Jungler"
    },
    "61-A9-B3-17-6C": {
        "name": "ACYRA",
        "studentID": "992676767",
        "major": "Mid-Laner"
    }
}

def match_student(uid_str):
    if uid_str in students:
        student = students[uid_str]
        print("VALID STUDENT")
        print("Name:", student["name"])
        print("ID:", student["studentID"])
        print("Major:", student["major"])
        return student
    else:
        print("UNKNOWN CARD")
        return None

# ============================================================
# MAIN
# ============================================================
wifi_connected = connect_wifi()
if wifi_connected:
    sync_time()

sd_ready = init_sd()

print("Scan RFID...")

while True:
    (stat, tag_type) = rdr.request(rdr.REQIDL)

    if stat == rdr.OK:
        (stat, raw_uid) = rdr.anticoll()
        if stat == rdr.OK:
            uid_str = "-".join("{:02X}".format(b) for b in raw_uid)
            print("\nCard UID:", uid_str)

            student = match_student(uid_str)
            now_str = get_datetime_str()
            print("Timestamp:", now_str)

            if student:
                buzz(0.3)
                if sd_ready:
                    save_to_sd(uid_str, student, now_str)
                if wifi_connected:
                    send_to_firestore(uid_str, student, now_str)
            else:
                print("Unknown Card")
                buzz(3)

            time.sleep(1)