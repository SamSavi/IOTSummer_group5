from machine import Pin
import dht
import time

# ── Hardware Setup ───────────────────────────────────────────────
sensor = dht.DHT22(Pin(16))   # DHT22 data pin connected to D4

print("DHT22 Sensor Reading Started...")
print("---------------------------")

# ── Main Loop ────────────────────────────────────────────────────
while True:
    try:
        sensor.measure()

        temperature = sensor.temperature()   # °C
        humidity    = sensor.humidity()       # %

        print("Temperature: {:.2f} °C".format(temperature))
        print("Humidity:    {:.2f} %".format(humidity))
        print("---------------------------")

    except OSError:
        print("Failed to read from DHT22 sensor")

    time.sleep(5)   # Read every 5 seconds