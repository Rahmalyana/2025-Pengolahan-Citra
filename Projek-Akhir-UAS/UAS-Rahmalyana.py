# FINAL
# Rahmalyana_4.33.23.1.20_TI2B

import cv2
import random
import time
import math
import numpy as np
from cvzone.HandTrackingModule import HandDetector
import cvzone

# Setup webcam
cap = cv2.VideoCapture(0)
cap.set(3, 1280)
cap.set(4, 720)

# Detektor tangan
detector = HandDetector(detectionCon=0.8, maxHands=1)

# Data konversi piksel ke cm
x_vals = [300, 245, 200, 170, 145, 130, 112, 103, 93, 87, 80, 75, 70, 67, 62, 59, 57]
y_vals = [20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 85, 90, 95, 100]
coff = np.polyfit(x_vals, y_vals, 2)

# Variabel game
score = 0
totalTime = 30
startTime = time.time()
pertanyaan = ''
opsi = []
tombol = []
terakhir_dipilih = None
jarak_target = 0
highlight_btn = None
highlight_time = 0


def buat_pertanyaan():
    global pertanyaan, opsi, tombol, terakhir_dipilih, jarak_target, highlight_btn, highlight_time
    semua_huruf = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
    pertanyaan = random.choice(semua_huruf) #pilih huruf acak
    opsi = random.sample(semua_huruf, 4) #menampilkan 4 huruf acak
    if pertanyaan not in opsi:
        opsi[random.randint(0, 3)] = pertanyaan

    tombol = []
    posisi = []
    jarak_target = random.randint(30, 60)
    # tombol tampil secara acak
    while len(tombol) < len(opsi):
        new_x = random.randint(150, 1100)
        new_y = random.randint(150, 500)

        overlap = False #cegah tombol menumpuk
        for ox, oy in posisi:
            if abs(new_x - ox) < 120 and abs(new_y - oy) < 120:
                overlap = True
                break
        if not overlap:
            posisi.append((new_x, new_y))
            tombol.append((opsi[len(tombol)], (new_x, new_y)))

    terakhir_dipilih = None
    highlight_btn = None
    highlight_time = 0

# Pertanyaan pertama
buat_pertanyaan()

while True:
    success, img = cap.read()
    img = cv2.flip(img, 1)

    waktu_tersisa = int(totalTime - (time.time() - startTime))
    if waktu_tersisa <= 0:
        cvzone.putTextRect(img, f'Waktu Habis!', (450, 200), scale=3, thickness=3)
        cvzone.putTextRect(img, f'Skor Akhir: {score}', (450, 300), scale=2)
        cvzone.putTextRect(img, 'Tekan R untuk Ulang', (450, 400), scale=2)
        cvzone.putTextRect(img, 'Tekan Q untuk Keluar', (900, 600), scale=2)
    else:
        tangan, img = detector.findHands(img, draw=False)
        if tangan:
            tangan = tangan[0]
            lmList = tangan['lmList']
            x1, y1 = lmList[5][:2]
            x2, y2 = lmList[17][:2]

            # Hitung jarak tangan
            distance = int(math.sqrt((x2 - x1)**2 + (y2 - y1)**2))
            A, B, C = coff
            distanceCM = A * distance ** 2 + B * distance + C

            index_x, index_y = lmList[8][0:2] # jari telunjuk

            for btn, pos in tombol:
                bx, by = pos
                if bx - 50 < index_x < bx + 50 and by - 50 < index_y < by + 50:
                    if abs(distanceCM - jarak_target) < 15:
                        if btn == pertanyaan:
                            if terakhir_dipilih != btn:
                                highlight_btn = btn
                                highlight_time = time.time()
                                score += 1
                                terakhir_dipilih = btn
        else:
            terakhir_dipilih = None

        # Tampilkan soal
        cvzone.putTextRect(img, f'Sentuh Huruf: {pertanyaan}', (450, 50), scale=2, thickness=2)

        # Tampilkan tombol huruf
        for btn, pos in tombol:
            bx, by = pos
            if btn == highlight_btn and time.time() - highlight_time < 0.5:
                warna = (0, 255, 0)  # Hijau jika benar
            else:
                warna = (255, 0, 255)
            cv2.circle(img, pos, 50, warna, cv2.FILLED)
            cvzone.putTextRect(img, btn, (bx - 25, by - 25), scale=2, offset=10)

        # Tampilkan skor, waktu, dan jarak
        cvzone.putTextRect(img, f'Skor: {score}', (50, 50), scale=2)
        cvzone.putTextRect(img, f'Waktu: {waktu_tersisa}', (1000, 50), scale=2)
        cvzone.putTextRect(img, f'Jarak target: {int(jarak_target)} cm', (50, 100), scale=1.5)
        if tangan:
            cvzone.putTextRect(img, f'Jarak tangan: {int(distanceCM)} cm', (900, 100), scale=1.5)

        # Ganti soal jika sudah ditampilkan hijau selama 0.5 detik
        if highlight_btn and time.time() - highlight_time >= 0.5:
            buat_pertanyaan()

    cv2.imshow("Interactive Letter Game", img)
    key = cv2.waitKey(1)

    if key == ord('r'):
        score = 0
        startTime = time.time()
        buat_pertanyaan()

    if key == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
