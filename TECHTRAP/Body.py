# pose_standalone.py
import cv2, time, math, os
import mediapipe as mp

# ========= كلاس Detector متوافق مع إصدارات Mediapipe الحديثة =========
class poseDetector:
    def __init__(self, mode=False, smooth=True, detectionCon=0.5, trackCon=0.5, model_complexity=1):
        self.mode = mode
        self.smooth = smooth
        self.detectionCon = float(detectionCon)
        self.trackCon = float(trackCon)
        self.model_complexity = int(model_complexity)

        self.mpDraw = mp.solutions.drawing_utils
        self.mpPose = mp.solutions.pose
        # التواقيع الحديثة:
        self.pose = self.mpPose.Pose(
            static_image_mode=self.mode,
            model_complexity=self.model_complexity,
            smooth_landmarks=self.smooth,
            enable_segmentation=False,
            smooth_segmentation=True,
            min_detection_confidence=self.detectionCon,
            min_tracking_confidence=self.trackCon,
        )
        self.results = None
        self.lmList = []

    def findPose(self, img, draw=True):
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.pose.process(imgRGB)
        if self.results.pose_landmarks and draw:
            self.mpDraw.draw_landmarks(img, self.results.pose_landmarks, self.mpPose.POSE_CONNECTIONS)
        return img

    def findPosition(self, img, draw=True):
        self.lmList = []
        if self.results and self.results.pose_landmarks:
            h, w, _ = img.shape
            for id, lm in enumerate(self.results.pose_landmarks.landmark):
                cx, cy = int(lm.x * w), int(lm.y * h)
                self.lmList.append([id, cx, cy])
                if draw:
                    cv2.circle(img, (cx, cy), 4, (255, 0, 0), cv2.FILLED)
        return self.lmList

    def findAngle(self, img, p1, p2, p3, draw=True):
        x1, y1 = self.lmList[p1][1:]
        x2, y2 = self.lmList[p2][1:]
        x3, y3 = self.lmList[p3][1:]
        angle = math.degrees(math.atan2(y3 - y2, x3 - x2) - math.atan2(y1 - y2, x1 - x2))
        if angle < 0: angle += 360
        if draw:
            cv2.line(img, (x1, y1), (x2, y2), (255,255,255), 2)
            cv2.line(img, (x3, y3), (x2, y2), (255,255,255), 2)
            for (x,y) in [(x1,y1),(x2,y2),(x3,y3)]:
                cv2.circle(img, (x,y), 6, (0,0,255), cv2.FILLED)
                cv2.circle(img, (x,y),12, (0,0,255), 2)
            cv2.putText(img, str(int(angle)), (x2-40, y2+40), cv2.FONT_HERSHEY_PLAIN, 2, (0,0,255), 2)
        return angle

# ========= ديمو تشغيل مستقل =========
def main():
    # جرّب هذه المسارات بالترتيب، وإلا استخدم الويبكام
    candidates = [
        "PoseVideos/3.mp4",
        "PoseVideos/1.mp4",
        "PoseVideos/9.mp4",
    ]
    cap = None
    for p in candidates:
        if os.path.exists(p):
            cap = cv2.VideoCapture(p)
            print(f"[INFO] Using video: {p}")
            break
    if cap is None:
        print("[WARN] Video not found. Falling back to webcam...")
        cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

    if not cap.isOpened():
        raise SystemExit("[ERR] Could not open video/webcam")

    detector = poseDetector(detectionCon=0.6, trackCon=0.5)
    pTime = 0

    while True:
        ok, img = cap.read()
        if not ok:
            print("[INFO] End of stream.")
            break

        img = detector.findPose(img, draw=True)
        lmList = detector.findPosition(img, draw=False)

        # مثال: قياس زاوية الكوع الأيمن (المفاصل 11-13-15 حسب mediapipe)
        if len(lmList) > 15:
            detector.findAngle(img, 11, 13, 15, draw=True)

        cTime = time.time()
        fps = 1 / (cTime - pTime) if (cTime - pTime) else 0
        pTime = cTime
        cv2.putText(img, f"{int(fps)} FPS", (20, 60), cv2.FONT_HERSHEY_PLAIN, 2, (50, 255, 50), 2)

        cv2.imshow("Pose Demo", img)
        key = cv2.waitKey(1) & 0xFF
        if key in [27, ord('q')]:  # ESC أو q
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
