from machine import Pin, I2C
import neopixel
import time
import tcs34725

# TCS34725 sensor
i2c = I2C(0, scl=Pin(22), sda=Pin(21))
sensor = tcs34725.TCS34725(i2c)

# NeoPixel ring on D23, 16 LEDs
led = neopixel.NeoPixel(Pin(23), 16)

def set_all_leds(r, g, b):
    for i in range(16):
        led[i] = (r, g, b)
    led.write()

print("Task 3: NeoPixel color control")

while True:
    r, g, b, c = sensor.read_raw()

    if r > g and r > b:
        color = "RED"
        set_all_leds(255, 0, 0)

    elif g > r and g > b:
        color = "GREEN"
        set_all_leds(0, 255, 0)

    elif b > r and b > g:
        color = "BLUE"
        set_all_leds(0, 0, 255)

    else:
        color = "UNKNOWN"
        set_all_leds(0, 0, 0)

    print("R:", r, "G:", g, "B:", b, "Color:", color)

    time.sleep(1)