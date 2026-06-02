import utime
from machine import I2C, Pin

LCD_ADDR    = 0x27
LCD_CHR     = 1
LCD_CMD     = 0
LCD_BACKLIGHT = 0x08
ENABLE      = 0b00000100

def lcd_byte(i2c, bits, mode):
    bits_high = mode | (bits & 0xF0) | LCD_BACKLIGHT
    bits_low  = mode | ((bits << 4) & 0xF0) | LCD_BACKLIGHT
    i2c.writeto(LCD_ADDR, bytes([bits_high]))
    lcd_toggle_enable(i2c, bits_high)
    i2c.writeto(LCD_ADDR, bytes([bits_low]))
    lcd_toggle_enable(i2c, bits_low)

def lcd_toggle_enable(i2c, bits):
    utime.sleep_us(500)
    i2c.writeto(LCD_ADDR, bytes([bits | ENABLE]))
    utime.sleep_us(500)
    i2c.writeto(LCD_ADDR, bytes([bits & ~ENABLE]))
    utime.sleep_us(500)

def lcd_init(i2c):
    for cmd in [0x33, 0x32, 0x06, 0x0C, 0x28, 0x01]:
        lcd_byte(i2c, cmd, LCD_CMD)
        utime.sleep_ms(5)

def lcd_clear(i2c):
    lcd_byte(i2c, 0x01, LCD_CMD)
    utime.sleep_ms(2)

def lcd_write(i2c, text, line):
    addr = 0x80 if line == 1 else 0xC0
    lcd_byte(i2c, addr, LCD_CMD)
    for ch in text[:16]:
        lcd_byte(i2c, ord(ch), LCD_CHR)