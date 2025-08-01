# virtual_calculator.py

import cv2
import mediapipe as mp
import numpy as np
import math

# Calculator UI setup
buttons = [
    ['7', '8', '9', '+'],
    ['4', '5', '6', '-'],
    ['1', '2', '3', '*'],
    ['0', 'C', '=', '/']
]

button_size = 80
panel_x, panel_y = 800, 100
expression = ""

# MediaPipe hand tracking
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7)

cap = cv2.VideoCapture(0)
cap.set(3, 1280)
cap.set(4, 720)

clicked = False
click_delay = 0

hand_landmarks_to_draw = None

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)

    # Prepare overlay for transparent panel
    overlay = frame.copy()
    alpha = 0.6

    # Draw calculator buttons on overlay
    for i in range(4):
        for j in range(4):
            x = panel_x + j * button_size
            y = panel_y + i * button_size
            cv2.rectangle(overlay, (x, y), (x + button_size, y + button_size), (0, 0, 0), -1)
            cv2.putText(overlay, buttons[i][j], (x + 20, y + 55), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 255, 0), 3)

    # Draw expression area on overlay
    cv2.rectangle(overlay, (panel_x, panel_y + 330), (panel_x + 320, panel_y + 390), (0, 0, 0), -1)
    cv2.putText(overlay, expression, (panel_x + 10, panel_y + 375), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 255), 3)

    # Process hand landmarks (do not draw yet)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb)
    index_finger = None
    thumb_tip = None

    if result.multi_hand_landmarks:
        hand_landmarks_to_draw = result.multi_hand_landmarks[0]
        h, w, _ = frame.shape
        index_finger = (int(hand_landmarks_to_draw.landmark[8].x * w), int(hand_landmarks_to_draw.landmark[8].y * h))
        thumb_tip = (int(hand_landmarks_to_draw.landmark[4].x * w), int(hand_landmarks_to_draw.landmark[4].y * h))

    # Blend overlay onto frame
    cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)

    # Draw hand landmarks after overlay
    if hand_landmarks_to_draw:
        mp_drawing.draw_landmarks(frame, hand_landmarks_to_draw, mp_hands.HAND_CONNECTIONS)

    # Detect click gesture
    if index_finger and thumb_tip:
        ix, iy = index_finger
        tx, ty = thumb_tip
        cv2.circle(frame, index_finger, 10, (0, 255, 0), -1)
        distance = math.hypot(ix - tx, iy - ty)

        if distance < 40 and click_delay == 0:
            cx = ix - panel_x
            cy = iy - panel_y

            if 0 <= cx < 320 and 0 <= cy < 320:
                col = cx // button_size
                row = cy // button_size
                val = buttons[int(row)][int(col)]

                if val == 'C':
                    expression = ""
                elif val == '=':
                    try:
                        expression = str(eval(expression))
                    except:
                        expression = "Error"
                else:
                    expression += val

                clicked = True
                click_delay = 20

    # Click cooldown
    if click_delay > 0:
        click_delay -= 1

    # Show the frame
    cv2.imshow("Virtual Calculator", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
