# ai_virtual_mouse_onefile.py
import cv2, time, math, numpy as np
import mediapipe as mp

# ========= تحكم الماوس: autopy -> pyautogui (fallback) =========
M_BACKEND = None
def _init_mouse_backend():
    global M_BACKEND, move_mouse, mouse_click, get_screen_size
    try:
        import autopy
        M_BACKEND = "autopy"
        def move_mouse(x, y): autopy.mouse.move(x, y)
        def mouse_click(): autopy.mouse.click()
        def get_screen_size(): return autopy.screen.size()
    except Exception:
        import pyautogui
        M_BACKEND = "pyautogui"
        def move_mouse(x, y): pyautogui.moveTo(x, y)
        def mouse_click(): pyautogui.click()
        def get_screen_size(): return pyautogui.size()
_init_mouse_backend()

# ========= نسخة محدثة من HandTrackingModule في نفس الملف =========
class handDetector:
    def __init__(self, mode=False, maxHands=1, detectionCon=0.7, trackCon=0.6):
        self.mode = mode
        self.maxHands = maxHands
        self.detectionCon = float(detectionCon)
        self.trackCon = float(trackCon)

        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands(
            static_image_mode=self.mode,
            max_num_hands=self.maxHands,
            min_detection_confidence=self.detectionCon,
            min_tracking_confidence=self.trackCon,
            model_complexity=1
        )
        self.mpDraw = mp.solutions.drawing_utils
        self.results = None
        self.lmList = []
        self.tipIds = [4, 8, 12, 16, 20]

    def findHands(self, img, draw=True):
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(imgRGB)
        if draw and self.results.multi_hand_landmarks:
            for handLms in self.results.multi_hand_landmarks:
                self.mpDraw.draw_landmarks(img, handLms, self.mpHands.HAND_CONNECTIONS)
        return img

    def findPosition(self, img, handNo=0, draw=True):
        self.lmList = []
        bbox = []
        if self.results and self.results.multi_hand_landmarks:
            if handNo >= len(self.results.multi_hand_landmarks):
                return self.lmList, bbox
            myHand = self.results.multi_hand_landmarks[handNo]
            h, w, _ = img.shape
            xList, yList = [], []
            for id, lm in enumerate(myHand.landmark):
                cx, cy = int(lm.x * w), int(lm.y * h)
                xList.append(cx); yList.append(cy)
                self.lmList.append([id, cx, cy])
                if draw:
                    cv2.circle(img, (cx, cy), 5, (255, 0, 255), cv2.FILLED)
            if xList and yList:
                xmin, xmax = min(xList), max(xList)
                ymin, ymax = min(yList), max(yList)
                bbox = [xmin, ymin, xmax, ymax]
                if draw:
                    cv2.rectangle(img, (xmin - 20, ymin - 20), (xmax + 20, ymax + 20),
                                  (0, 255, 0), 2)
        return self.lmList, bbox

    def fingersUp(self):
        fingers = []
        if not self.lmList:
            return fingers
        # الإبهام (تعتمد على اتجاه الكاميرا؛ لو اتجاهك معاكس اعكس > إلى <)
        fingers.append(1 if self.lmList[self.tipIds[0]][1] > self.lmList[self.tipIds[0]-1][1] else 0)
        # باقي الأصابع
        for i in range(1, 5):
            fingers.append(1 if self.lmList[self.tipIds[i]][2] < self.lmList[self.tipIds[i]-2][2] else 0)
        return fingers

    def findDistance(self, p1, p2, img, draw=True, r=15, t=3):
        x1, y1 = self.lmList[p1][1:]
        x2, y2 = self.lmList[p2][1:]
        cx, cy = (x1 + x2)//2, (y1 + y2)//2
        if draw:
            cv2.line(img, (x1, y1), (x2, y2), (255, 0, 255), t)
            for (x, y), col in [((x1, y1),(255,0,255)), ((x2, y2),(255,0,255)), ((cx, cy),(0,255,0))]:
                cv2.circle(img, (x, y), r, col, cv2.FILLED)
        length = math.hypot(x2 - x1, y2 - y1)
        return length, img, [x1, y1, x2, y2, cx, cy]

# ========= فتح الكاميرا بمحاولات متعددة (index/backends) =========
def open_camera_set(w, h):
    attempts = [
        (1, cv2.CAP_DSHOW), (1, cv2.CAP_MSMF), (1, cv2.CAP_ANY),  # جرّب أولاً index=1 (زي الأصل)
        (0, cv2.CAP_DSHOW), (0, cv2.CAP_MSMF), (0, cv2.CAP_ANY),
    ]
    for idx, be in attempts:
        cap = cv2.VideoCapture(idx, be)
        cap.set(3, w); cap.set(4, h)
        time.sleep(0.2)
        ok = cap.isOpened()
        print(f"Try camera index={idx}, backend={be} -> opened={ok}")
        if ok:
            print(f"[OK] Using camera index={idx} backend={be}")
            return cap
        cap.release()
    return None

def main():
    # إعدادات من كودك الأصلي
    wCam, hCam = 640, 480
    frameR = 100   # إطار التحكم
    smoothening = 7

    pTime = 0
    plocX, plocY = 0, 0
    clocX, clocY = 0, 0
    control_on = True  # toggle بالزر t

    # فتح الكاميرا
    cap = open_camera_set(wCam, hCam)
    if cap is None:
        print("[ERR] Could not open any camera. تأكد من الأذونات وأغلق البرامج التي تستخدم الكاميرا.")
        return

    detector = handDetector(maxHands=1)
    wScr, hScr = get_screen_size()

    cv2.namedWindow("Image", cv2.WINDOW_AUTOSIZE)

    while True:
        # 1) التقاط الإطار
        success, img = cap.read()
        if not success:
            print("[INFO] End of stream / failed to read frame.")
            break

        # 2) اكتشاف اليد والمعالم
        img = detector.findHands(img)
        lmList, bbox = detector.findPosition(img)

        # 3) لو في يد: خذ رؤوس السبابة والوسطى
        if len(lmList) != 0:
            x1, y1 = lmList[8][1:]
            x2, y2 = lmList[12][1:]
        else:
            x1 = y1 = x2 = y2 = None

        # 4) حالة الأصابع
        fingers = detector.fingersUp() if lmList else []

        # 5) مستطيل منطقة التحكم
        cv2.rectangle(img, (frameR, frameR), (wCam - frameR, hCam - frameR),
                      (255, 0, 255), 2)

        # 6) وضع الحركة: سبابة مرفوعة فقط
        if control_on and lmList and len(fingers) >= 3 and fingers[1] == 1 and fingers[2] == 0:
            # تحويل الإحداثيات
            x3 = np.interp(x1, (frameR, wCam - frameR), (0, wScr))
            y3 = np.interp(y1, (frameR, hCam - frameR), (0, hScr))
            # تنعيم
            clocX = plocX + (x3 - plocX) / smoothening
            clocY = plocY + (y3 - plocY) / smoothening

            # تحريك الماوس (انعكاس أفقي wScr - clocX؛ احذف الانعكاس لو تبغى)
            move_mouse(wScr - clocX, clocY)
            cv2.circle(img, (x1, y1), 15, (255, 0, 255), cv2.FILLED)
            plocX, plocY = clocX, clocY

        # 7) وضع النقر: سبابة + وسطى
        if control_on and lmList and len(fingers) >= 3 and fingers[1] == 1 and fingers[2] == 1:
            length, img, lineInfo = detector.findDistance(8, 12, img)
            if length < 40:
                cv2.circle(img, (lineInfo[4], lineInfo[5]), 15, (0, 255, 0), cv2.FILLED)
                mouse_click()
                time.sleep(0.05)  # debounce بسيط

        # 8) FPS
        cTime = time.time()
        fps = 1 / (cTime - pTime) if (cTime - pTime) else 0
        pTime = cTime
        cv2.putText(img, f"{int(fps)} FPS [{M_BACKEND}]", (20, 35),
                    cv2.FONT_HERSHEY_PLAIN, 2, (255, 255, 255), 2)
        cv2.putText(img, "q/ESC: quit | t: toggle control", (20, 65),
                    cv2.FONT_HERSHEY_PLAIN, 1, (220, 220, 220), 1)
        cv2.putText(img, f"control: {'ON' if control_on else 'OFF'}", (20, 90),
                    cv2.FONT_HERSHEY_PLAIN, 1, (0,255,0) if control_on else (0,0,255), 2)

        # 9) عرض
        cv2.imshow("Image", img)
        key = cv2.waitKey(1) & 0xFF
        if key in (27, ord('q')):
            break
        if key == ord('t'):
            control_on = not control_on

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
