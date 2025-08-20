# basketball_demo.py
import cv2, math, numpy as np
import cvzone
from cvzone.ColorModule import ColorFinder
import os

# ===== إعداد الفيديو =====
# غيّر المسار هنا لو لزم
VIDEO_PATHS = [
    "Resources/Videos/vid (4).mp4",
    "Videos/vid (4).mp4",
    "vid (4).mp4"
]
cap = None
for p in VIDEO_PATHS:
    if os.path.exists(p):
        cap = cv2.VideoCapture(p)
        print(f"[INFO] Using video: {p}")
        break
if cap is None:
    print("[WARN] Video not found. Falling back to webcam...")
    cap = cv2.VideoCapture(0)
if not cap.isOpened():
    raise SystemExit("[ERR] Could not open video/webcam")

# ===== كاشف اللون (اضبط القيم حسب كرة الفيديو لديك) =====
myColorFinder = ColorFinder(False)
hsvVals = {'hmin': 8, 'smin': 124, 'vmin': 13, 'hmax': 24, 'smax': 255, 'vmax': 255}

# ===== متغيرات =====
posListX, posListY = [], []
xList = list(range(0, 1300))
start = True          # يبدأ تشغيل
prediction = False

def predict_basket(coff, y_hoop=593, x_min=330, x_max=430):
    """يرجع True لو توقّع أن الكرة تقطع السلة (المستوى y_hoop بين x_min..x_max)."""
    a, b, c = coff
    c = c - y_hoop
    disc = b*b - 4*a*c
    if disc < 0:     # لا تقاطع
        return False
    x = int((-b - math.sqrt(disc)) / (2 * a))
    return x_min < x < x_max

while True:
    if start:  # وضع التشغيل (لو False يوقف على آخر إطار)
        success, img = cap.read()
        if not success:
            print("[INFO] End of video / camera read failed.")
            break

        # قص علوي مثل الدرس
        if img.shape[0] > 900:
            img = img[0:900, :]

        imgPrediction = img.copy()
        imgResult = img.copy()

        # إيجاد الكرة باللون
        imgBall, mask = myColorFinder.update(img, hsvVals)

        # إيجاد الكونتور الأكبر
        imgCon, contours = cvzone.findContours(img, mask, minArea=200)
        if contours:
            cx, cy = contours[0]['center']
            posListX.append(cx)
            posListY.append(cy)

        # رسم المسار والتوقّع
        if len(posListX) >= 2:
            # معامل القطع المكافئ y = a x^2 + b x + c
            # نحتاج >=3 نقاط للحصول على منحنًى مستقر
            if len(posListX) >= 3:
                coff = np.polyfit(posListX, posListY, 2)
            else:
                coff = np.polyfit(posListX + [posListX[-1]+1], posListY + [posListY[-1]], 2)

            # نقاط المسار الفعلية
            for i, (px, py) in enumerate(zip(posListX, posListY)):
                cv2.circle(imgCon, (px, py), 10, (0, 255, 0), cv2.FILLED)
                cv2.circle(imgResult, (px, py), 10, (0, 255, 0), cv2.FILLED)
                if i > 0:
                    cv2.line(imgCon, (posListX[i-1], posListY[i-1]), (px, py), (0, 255, 0), 2)
                    cv2.line(imgResult, (posListX[i-1], posListY[i-1]), (px, py), (0, 255, 0), 2)

            # المنحنى المتوقع
            for x in xList:
                y = int(coff[0]*x**2 + coff[1]*x + coff[2])
                cv2.circle(imgPrediction, (x, y), 2, (255, 0, 255), cv2.FILLED)
                cv2.circle(imgResult,     (x, y), 2, (255, 0, 255), cv2.FILLED)

            # التنبؤ (قبل اكتمال المسار)
            if len(posListX) < 10:
                prediction = predict_basket(coff, y_hoop=593, x_min=330, x_max=430)

            # كتابة النتيجة
            cvzone.putTextRect(
                imgResult,
                "Basket" if prediction else "No Basket",
                (50, 150),
                scale=5, thickness=8,
                colorR=(0, 200, 0) if prediction else (0, 0, 200),
                offset=20
            )

        # رسم خط السلة المرجعي
        cv2.line(imgCon, (330, 593), (430, 593), (255, 0, 255), 10)
        out = cv2.resize(imgResult, None, fx=0.7, fy=0.7)
        cv2.imshow("Basketball", out)

        # بعد 10 نقاط يوقف تلقائيًا (مثل نسخة الدرس الثانية)
        if len(posListX) == 10:
            start = False

    key = cv2.waitKey(40) & 0xFF
    if key == ord('q') or key == 27:
        break
    if key == ord('s'):
        start = True  # استئناف
    if key == ord('c'):
        posListX.clear(); posListY.clear(); prediction = False  # مسح المسار

cap.release()
cv2.destroyAllWindows()
