
import threading
import time
import cv2
import numpy as np
import cvzone
from cvzone.HandTrackingModule import HandDetector
import tkinter as tk
from PIL import Image, ImageTk  
import os

# استيراد الواجهة
from GUI import build_ui  # تأكد أن ملف GUI.py في نفس المجلد

# استيراد مباشر كموديولات لتفادي تعارض الأسماء
import directkeys1 as dk1   # يحتوي enter_pressed
import directkeys2 as dk2   # يحتوي right_pressed, left_pressed
import directkeys3 as dk3   # يحتوي space_pressed


# =========================
#        GAME 1
# =========================
def game1():
    print("Game 1 Selected")
    detector = HandDetector(detectionCon=0.5, maxHands=1)
    enter_key = dk1.enter_pressed

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Camera not available")
        return
    time.sleep(1.0)

    current_keys = set()
    try:
        while True:
            ok, frame = cap.read()
            if not ok:
                break

            # معالجة الإطار
            hands, img = detector.findHands(frame)  # img هو نفس frame بعد الرسم
            cv2.rectangle(img, (0, 425), (300, 480), (50, 50, 255), -1)
            cv2.rectangle(img, (400, 425), (640, 480), (50, 50, 255), -1)

            if hands:
                lm = hands[0]
                finger_up = detector.fingersUp(lm)
                # قبضة = قفزة
                if finger_up == [0, 0, 0, 0, 0]:
                    cv2.putText(img, 'Jump', (440, 460),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 255), 2)
                    dk1.PressKey(enter_key)
                    current_keys.add(enter_key)
                else:
                    for k in list(current_keys):
                        dk1.ReleaseKey(k)
                    current_keys.clear()
            else:
                for k in list(current_keys):
                    dk1.ReleaseKey(k)
                current_keys.clear()

            cv2.imshow("Game 1", img)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    finally:
        for k in list(current_keys):
            dk1.ReleaseKey(k)
        cap.release()
        cv2.destroyAllWindows()


def start_game1():
    t = threading.Thread(target=game1, daemon=True)
    t.start()         
# =========================
#        GAME 2
# =========================
def game2_race():
    print("Game 2 Selected")
    brake_key = dk2.left_pressed
    gas_key = dk2.right_pressed

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Camera not available")
        return

    detector = HandDetector(detectionCon=0.7, maxHands=1)
    time.sleep(1.0)

    try:
        while True:
            ok, img = cap.read()
            if not ok:
                break

            hands, img = detector.findHands(img)
            if hands:
                fingers = detector.fingersUp(hands[0])
                if fingers == [0, 0, 0, 0, 0]:        # brake
                    dk2.PressKey(brake_key); dk2.ReleaseKey(gas_key)
                elif fingers == [1, 1, 1, 1, 1]:     # gas
                    dk2.PressKey(gas_key); dk2.ReleaseKey(brake_key)
                else:
                    dk2.ReleaseKey(brake_key); dk2.ReleaseKey(gas_key)
            else:
                dk2.ReleaseKey(brake_key); dk2.ReleaseKey(gas_key)

            cv2.imshow("Race Game", img)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    finally:
        dk2.ReleaseKey(brake_key); dk2.ReleaseKey(gas_key)
        cap.release()
        cv2.destroyAllWindows()


def start_game2():
    t = threading.Thread(target=game2_race, daemon=True)
    t.start()


# =========================
#        GAME 3
# =========================
def game3():
    print("Game 3 Selected")
    detector = HandDetector(detectionCon=0.8, maxHands=1)
    space_key = dk3.space_pressed

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Camera not available")
        return
    time.sleep(1.0)

    current_keys = set()
    try:
        while True:
            ok, frame = cap.read()
            if not ok:
                break

            hands, img = detector.findHands(frame)
            if hands:
                lm = hands[0]
                finger_up = detector.fingersUp(lm)
                if finger_up == [0, 0, 0, 0, 0]:
                    dk3.PressKey(space_key)
                    current_keys.add(space_key)
                else:
                    for k in list(current_keys):
                        dk3.ReleaseKey(k)
                    current_keys.clear()
            else:
                for k in list(current_keys):
                    dk3.ReleaseKey(k)
                current_keys.clear()

            cv2.imshow("Game 3", img)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    finally:
        for k in list(current_keys):
            dk3.ReleaseKey(k)
        cap.release()
        cv2.destroyAllWindows()


def start_game3():
    t = threading.Thread(target=game3, daemon=True)
    t.start()

# =========================
#        GAME 4 (Pong)
# =========================
def game4():

    print("Game 4 Selected")
    cap = cv2.VideoCapture(0)
    cap.set(3, 1280)
    cap.set(4, 720)

    # Importing all images
    imgBackground = cv2.imread("Resources/Background.png")
    imgGameOver = cv2.imread("Resources/gameOver.png")
    imgBall = cv2.imread("Resources/Ball.png", cv2.IMREAD_UNCHANGED)
    imgBat1 = cv2.imread("Resources/bat1.png", cv2.IMREAD_UNCHANGED)
    imgBat2 = cv2.imread("Resources/bat2.png", cv2.IMREAD_UNCHANGED)

    # Hand Detector
    detector = HandDetector(detectionCon=0.8, maxHands=2)

    # Variables
    ballPos = [100, 100]
    speedX = 15
    speedY = 15
    gameOver = False
    score = [0, 0]

    while True:
        _, img = cap.read()
        img = cv2.flip(img, 1)
        imgRaw = img.copy()

        # Find the hand and its landmarks
        hands, img = detector.findHands(img, flipType=False)  # with draw

        # Overlaying the background image
        img = cv2.addWeighted(img, 0.2, imgBackground, 0.8, 0)

        # Check for hands
        if hands:
            for hand in hands:
                x, y, w, h = hand['bbox']
                h1, w1, _ = imgBat1.shape
                y1 = y - h1 // 2
                y1 = np.clip(y1, 20, 415)

                if hand['type'] == "Left":
                    img = cvzone.overlayPNG(img, imgBat1, (59, y1))
                    if 59 < ballPos[0] < 59 + w1 and y1 < ballPos[1] < y1 + h1:
                        speedX = -speedX
                        ballPos[0] += 30
                        score[0] += 1

                if hand['type'] == "Right":
                    img = cvzone.overlayPNG(img, imgBat2, (1195, y1))
                    if 1195 - 50 < ballPos[0] < 1195 and y1 < ballPos[1] < y1 + h1:
                        speedX = -speedX
                        ballPos[0] -= 30
                        score[1] += 1

        # Game Over
        if ballPos[0] < 40 or ballPos[0] > 1200:
            gameOver = True

        if gameOver:
            img = imgGameOver
            cv2.putText(img, str(score[1] + score[0]).zfill(2), (585, 360), cv2.FONT_HERSHEY_COMPLEX,
                        2.5, (200, 0, 200), 5)

        # If game not over move the ball
        else:

            # Move the Ball
            if ballPos[1] >= 500 or ballPos[1] <= 10:
                speedY = -speedY

            ballPos[0] += speedX
            ballPos[1] += speedY

            # Draw the ball
            img = cvzone.overlayPNG(img, imgBall, ballPos)

            cv2.putText(img, str(score[0]), (300, 650), cv2.FONT_HERSHEY_COMPLEX, 3, (255, 255, 255), 5)
            cv2.putText(img, str(score[1]), (900, 650), cv2.FONT_HERSHEY_COMPLEX, 3, (255, 255, 255), 5)

        img[580:700, 20:233] = cv2.resize(imgRaw, (213, 120))

        cv2.imshow("Image", img)
        key = cv2.waitKey(1)
        if key == ord('r'):
            ballPos = [100, 100]
            speedX = 15
            speedY = 15
            gameOver = False
            score = [0, 0]
            imgGameOver = cv2.imread("Resources/gameOver.png")
        if key == ord('q'):
            break
    pass
def start_game4():
    threading.Thread(target=game4, daemon=True).start()
# =========================
#     MAIN (single Tk)
# =========================
if __name__ == "__main__":
    root = tk.Tk()
    # مرّر callbacks للواجهة
    build_ui(root, on_game1=start_game1, on_game2=start_game2, on_game3=start_game3, on_game4=start_game4)
    root.mainloop()