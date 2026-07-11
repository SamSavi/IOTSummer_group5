from machine import Pin, I2C, PWM
import neopixel
import time
import tcs34725

# TCS34725 sensor
i2c = I2C(0, scl=Pin(22), sda=Pin(21))
sensor = tcs34725.TCS34725(i2c)

# NeoPixel ring
led = neopixel.NeoPixel(Pin(23), 16)

# Motor driver pins
ENA = PWM(Pin(14))
ENA.freq(1000)

IN1 = Pin(26, Pin.OUT)
IN2 = Pin(27, Pin.OUT)

def set_all_leds(r, g, b):
    for i in range(16):
        led[i] = (r, g, b)
    led.write()

def motor_forward(speed):
    IN1.value(1)
    IN2.value(0)
    ENA.duty(speed)

def motor_stop():
    IN1.value(0)
    IN2.value(0)
    ENA.duty(0)

print("Task 4: Motor PWM Control")

while True:
    r, g, b, c = sensor.read_raw()

    if r > g and r > b:
        color = "RED"
        set_all_leds(255, 0, 0)
        motor_forward(700)

    elif g > r and g > b:
        color = "GREEN"
        set_all_leds(0, 255, 0)
        motor_forward(500)

    elif b > r and b > g:
        color = "BLUE"
        set_all_leds(0, 0, 255)
        motor_forward(300)

    else:
        color = "UNKNOWN"
        set_all_leds(0, 0, 0)
        motor_stop()

    print("R:", r, "G:", g, "B:", b, "Color:", color)

    time.sleep(1)