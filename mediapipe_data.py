 # Limitação FPS

import cv2
import mediapipe as mp
import time
import math
import csv

class PoseDetector:
    def __init__(self, mode=False, model_complexity=1, smooth=True, detectionCon=0.5, trackCon=0.5):
        self.mode = mode
        self.model_complexity = model_complexity
        self.smooth = smooth
        self.detectionCon = detectionCon
        self.trackCon = trackCon

        self.mpPose = mp.solutions.pose
        self.pose = self.mpPose.Pose(
            static_image_mode=self.mode, 
            model_complexity=self.model_complexity,  
            smooth_landmarks=self.smooth, 
            min_detection_confidence=self.detectionCon, 
            min_tracking_confidence=self.trackCon
        )
        self.mpDraw = mp.solutions.drawing_utils
        self.mpDrawingStyles = mp.solutions.drawing_styles

    def findPose(self, img, draw=True):
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.pose.process(imgRGB)

        if self.results.pose_landmarks and draw:
            self.mpDraw.draw_landmarks(
                img, self.results.pose_landmarks, self.mpPose.POSE_CONNECTIONS,
                landmark_drawing_spec=self.mpDrawingStyles.get_default_pose_landmarks_style()
            )
        return img

    def findPosition(self, img, draw=True):
        lmList = []
        if self.results.pose_landmarks:
            for id, lm in enumerate(self.results.pose_landmarks.landmark):
                h, w, _ = img.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                lmList.append([id, cx, cy])

                if draw:
                    cv2.circle(img, (cx, cy), 5, (255, 0, 0), cv2.FILLED)

        return lmList

def findAngle(img, p1, p2, p3, draw=True):
    x1, y1 = p1[1], p1[2]
    x2, y2 = p2[1], p2[2]
    x3, y3 = p3[1], p3[2]

    angle = math.degrees(math.atan2(y3 - y2, x3 - x2) -
                         math.atan2(y1 - y2, x1 - x2))
    angle = abs(angle)
    if angle > 180:
        angle = 360 - angle

    return angle

def main():
    cap = cv2.VideoCapture(2) # mudar para zero
    detector = PoseDetector()
    
    max_fps = 30
    frame_interval = 1 / max_fps
    sampling_rate = 0.5
    last_sample_time = 0
    pTime = 0

    start_video_time = time.time()  # <<< início do vídeo para timestamp relativo

    # CSV
    csv_file = open('angulos_pernas.csv', mode='w', newline='')
    csv_writer = csv.writer(csv_file)
    csv_writer.writerow(['timestamp_s', 'angulo_perna_direita', 'angulo_perna_esquerda'])

    while cap.isOpened():
        start_time = time.time()

        success, img = cap.read()
        if not success:
            print("Falha ao capturar imagem da câmera")
            break

        img = detector.findPose(img)
        lmList = detector.findPosition(img, draw=False)

        cTime = time.time()
        fps = 1 / (cTime - pTime) if cTime - pTime > 0 else 0
        pTime = cTime
        cv2.putText(img, f'FPS: {int(fps)}', (10, 50),
                    cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 0), 2)

        # Só amostra se passou o tempo definido
        if cTime - last_sample_time >= sampling_rate and len(lmList) != 0:
            angle_right = round(findAngle(img, lmList[24], lmList[26], lmList[28]), 2)
            angle_left = round(findAngle(img, lmList[23], lmList[25], lmList[27]), 2)

            timestamp = round(cTime - start_video_time, 2)  # Tempo relativo ao início
            csv_writer.writerow([timestamp, angle_right, angle_left])
            last_sample_time = cTime

        cv2.imshow("MediaPipe Pose", img)

        elapsed = time.time() - start_time
        if elapsed < frame_interval:
            time.sleep(frame_interval - elapsed)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    csv_file.close()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()