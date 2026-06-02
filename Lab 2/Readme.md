# LAB 2 - IoT Webserver with LED, Sensors, and LCD Control

## Overview

This project implements an ESP32-based IoT system using MicroPython. The ESP32 hosts a web server that allows users to:

- Control an LED from a web browser
- Monitor temperature and humidity from a DHT22 sensor
- Monitor distance using an HC-SR04 ultrasonic sensor
- Display sensor values on a 16×2 I2C LCD
- Send custom text messages from the browser to the LCD

The system demonstrates interaction between web technologies and embedded hardware.

---

## Hardware Components

- ESP32 Development Board
- DHT22 Temperature & Humidity Sensor
- HC-SR04 Ultrasonic Sensor
- 16×2 LCD with I2C Backpack
- LED
- Breadboard and Jumper Wires
- Wi-Fi Connection

---

## Wiring

| Component | ESP32 Pin |
|------------|------------|
| LED | GPIO2 |
| DHT22 Data | GPIO4 |
| HC-SR04 Trig | GPIO27 |
| HC-SR04 Echo | GPIO26 |
| LCD SDA | GPIO21 |
| LCD SCL | GPIO22 |
| VCC | 5V |
| GND | GND |




## Files

### Lab 2 Task 1.py
Implements:
- Wi-Fi connection
- Web server
- LED ON/OFF control through browser buttons

### Lab 2 Task 2.py
Adds:
- DHT22 sensor readings
- Ultrasonic distance measurements
- Live sensor display on the web page

### Lab 2 Task 3.py
Adds:
- LCD integration
- Display temperature and humidity on LCD
- Display distance on LCD
- LCD display mode selection from browser

### Lab 2 Task 4.py
Adds:
- Textbox on webpage
- Send custom messages to LCD
- LCD text display mode

### lcd_i2c.py
LCD helper library used for:
- LCD initialization
- LCD writing
- LCD clearing
- I2C communication

---

## Setup

### 1. Install MicroPython

Flash MicroPython firmware onto the ESP32.

### 2. Upload Files

Upload the following files to the ESP32:

```text
Lab 2 task 4.py
lcd_i2c.py
```

### 3. Configure Wi-Fi

Edit:

```python
SSID = "Robotic WIFI"
PASSWORD = "rbtWIFI@2025"
```

Replace these values with your own Wi-Fi credentials if necessary.

### 4. Run Program

Run:

```text
Lab 2 task 4.py
```

The ESP32 will display its IP address in the Thonny shell.

Example:

```text
Connected: 192.168.1.50
```

Open this IP address in a web browser.

---

## Features

### Task 1 – LED Control

Users can:
- Turn LED ON
- Turn LED OFF

using web buttons.

Video: https://youtube.com/shorts/Z9jXVpKzv14?si=8pjWIcI7mM8MJ_PN

### Task 2 – Sensor Monitoring

The webpage displays:
- Temperature
- Humidity
- Distance

Sensor values automatically refresh every 2 seconds.

### Task 3 – LCD Control

Buttons available:
- Auto Mode
- Show Temperature & Humidity
- Show Distance

The LCD updates based on the selected mode.

### Task 4 – Custom LCD Message

Users can:
1. Enter text into a textbox
2. Press Send
3. Display custom text on the LCD

Messages longer than 16 characters continue onto the second LCD line.

Video: https://youtube.com/shorts/0VlYYBRJ-7Q?si=PN4__8WaRa8DkT0b

## How to Use

### LED Control

Press **Turn ON** to enable the LED.

Press **Turn OFF** to disable the LED.

### Temperature Display

Press **Show Temp + Humidity** to display sensor values on the LCD.

### Distance Display

Press **Show Distance** to display distance readings on the LCD.

### Custom Text

Enter a message in the textbox and click **Send to LCD**.

The text will appear on the LCD.

---

## Evidence

The repository includes:

- Source code
- Wiring diagram
- Screenshots of web interface
- LCD output photos
- Demo video

### Required Demonstrations

- LED ON/OFF from browser
- Temperature and humidity display
- Distance sensor display
- LCD temperature mode
- LCD distance mode
- Custom text sent to LCD

