import network
import socket

ssid = "Robotic WIFI"
password = "rbtWIFI@2025"

# Connect to WiFi
wifi = network.WLAN(network.STA_IF)
wifi.active(True)
wifi.connect(ssid, password)

print("Connecting", end="")
while not wifi.isconnected():
    pass

print("\nConnected!")
print("ESP32 IP:", wifi.ifconfig()[0])



def forward():
    print("Command: FORWARD")
    IN1.value(1)
    IN2.value(0)

def backward():
    print("Command: BACKWARD")
    IN1.value(0)
    IN2.value(1)

def stop():
    print("Command: STOP")
    IN1.value(0)
    IN2.value(0)

def set_speed(value):
    print("Speed value received:", value)
    


# ==== Web Server ====
addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
server = socket.socket()
server.bind(addr)
server.listen(5)

print("Server running on", addr)


while True:
    client, addr = server.accept()
    print("Client connected from", addr)

    request = client.recv(1024).decode()
    print("Request:", request)

    # ==== Parse Request ====
    if "GET /forward" in request:
        forward()
        response = "Forward received"

    elif "GET /backward" in request:
        backward()
        response = "Backward received"

    elif "GET /stop" in request:
        stop()
        response = "Stop received"

    elif "GET /speed" in request:
        # Extract value parameter
        try:
            value = request.split("value=")[1].split(" ")[0]
            set_speed(value)
        except:
            value = "None"
            print("No speed value")
        response = "Speed received"

    else:
        response = "Invalid command"

    
    client.send("HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\n\r\n")
    client.send(response)
    client.close()
