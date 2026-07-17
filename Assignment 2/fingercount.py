import cv2
import mediapipe as mp
import paho.mqtt.client as mqtt
import time

ESP32_CAM_URL = "http://10.30.0.170:81/stream"

MQTT_BROKER = "broker.hivemq.com"
MQTT_PORT = 1883
MQTT_TOPIC = "aupp/finger_led"

mqtt_client = mqtt.Client()
mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)

mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils


def count_fingers(hand_landmarks, hand_label):
    lm = hand_landmarks.landmark
    fingers = 0

    if hand_label == "Right":
        if lm[4].x < lm[3].x:
            fingers += 1
    else:
        if lm[4].x > lm[3].x:
            fingers += 1

    tips = [8, 12, 16, 20]
    pips = [6, 10, 14, 18]

    for tip, pip in zip(tips, pips):
        if lm[tip].y < lm[pip].y:
            fingers += 1

    return fingers


cap = cv2.VideoCapture(ESP32_CAM_URL)

last_command = ""
last_time = 0

with mp_hands.Hands(
    max_num_hands=1,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
) as hands:

    while True:
        success, frame = cap.read()

        if not success:
            print("Cannot read ESP32-CAM stream")
            break

        frame = cv2.flip(frame, 1)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(rgb)

        if results.multi_hand_landmarks:
            for hand_landmarks, handedness in zip(
                results.multi_hand_landmarks,
                results.multi_handedness
            ):
                mp_draw.draw_landmarks(
                    frame,
                    hand_landmarks,
                    mp_hands.HAND_CONNECTIONS
                )

                label = handedness.classification[0].label
                fingers = count_fingers(hand_landmarks, label)

                command = ""

                if fingers == 1:
                    command = "ON"
                elif fingers == 2:
                    command = "OFF"

                if command != "" and command != last_command and time.time() - last_time > 1:
                    mqtt_client.publish(MQTT_TOPIC, command)
                    print("Sent:", command)
                    last_command = command
                    last_time = time.time()

                cv2.putText(
                    frame,
                    f"Fingers: {fingers}",
                    (20, 60),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1.5,
                    (0, 255, 0),
                    3
                )

        cv2.imshow("ESP32-CAM Finger Count", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

cap.release()
cv2.destroyAllWindows()