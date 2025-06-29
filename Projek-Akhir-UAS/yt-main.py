import cv2
from cvzone.HandTrackingModule import HandDetector
import math
import numpy as np
import cvzone

# Webcam setup
cap = cv2.VideoCapture(0)
cap.set(3, 1280)
cap.set(4, 720)

# Hand detector
detector = HandDetector(detectionCon=0.8, maxHands=1)

# Data konversi piksel ke cm
x_vals = [300, 245, 200, 170, 145, 130, 112, 103, 93, 87, 80, 75, 70, 67, 62, 59, 57]
y_vals = [20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 85, 90, 95, 100]
coff = np.polyfit(x_vals, y_vals, 2)  # y = Ax^2 + Bx + C

# Main loop
while True:
    success, img = cap.read()
    if not success:
        print("Gagal membuka kamera.")
        break

    hands, img = detector.findHands(img, draw=False)
    if hands:
        hand = hands[0]
        lmList = hand["lmList"]
        x, y, w, h = hand["bbox"]

        x1, y1 = lmList[5][:2]
        x2, y2 = lmList[17][:2]

        # Hitung jarak
        distance = int(math.sqrt((x2 - x1)**2 + (y2 - y1)**2))

        # Konversi ke cm
        A, B, C = coff
        distanceCM = A * distance ** 2 + B * distance + C

        # Gambar kotak dan jarak
        cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 255), 3)
        cvzone.putTextRect(img, f'{int(distanceCM)} cm', (x + 5, y - 10))

    cv2.imshow("Image", img)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
