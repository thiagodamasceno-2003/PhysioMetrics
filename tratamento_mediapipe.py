 # Limitação FPS

# Bibliotecas usadas: visão computacional, deteção de pose, tempo, ângulos e CSV.
import cv2
import mediapipe as mp
import time
import math
import csv

# Classe que encapsula a deteção da pose e a extração das coordenadas do corpo.
class PoseDetector:
    # Inicializa o MediaPipe Pose e configura os parâmetros de deteção e seguimento.
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

    # Processa a imagem para detetar a pose e, opcionalmente, desenha o esqueleto.
    def findPose(self, img, draw=True):
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.pose.process(imgRGB)

        if self.results.pose_landmarks and draw:
            self.mpDraw.draw_landmarks(
                img, self.results.pose_landmarks, self.mpPose.POSE_CONNECTIONS,
                landmark_drawing_spec=self.mpDrawingStyles.get_default_pose_landmarks_style()
            )
        return img

    # Converte os pontos corporais detetados em coordenadas de píxeis (x, y).
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

# Calcula o ângulo formado por três pontos do corpo, usando o ponto p2 como vértice.
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

# Função principal: captura vídeo, calcula ângulos das pernas e guarda os dados.
def main():
    # Abre a câmara; alterar o índice (por exemplo, para 0) se necessário.
    cap = cv2.VideoCapture(2) # mudar para zero
    detector = PoseDetector()
    
    # Define o limite de processamento para cerca de 30 imagens por segundo.
    max_fps = 30
    frame_interval = 1 / max_fps
    sampling_rate = 0.5
    last_sample_time = 0
    pTime = 0

    # Guarda o instante inicial para calcular tempos relativos no CSV.
    start_video_time = time.time()  # <<< início do vídeo para timestamp relativo

    # Cria o ficheiro CSV e escreve os nomes das colunas.
    csv_file = open('angulos_pernas.csv', mode='w', newline='')
    csv_writer = csv.writer(csv_file)
    csv_writer.writerow(['timestamp_s', 'angulo_perna_direita', 'angulo_perna_esquerda'])

    # Processa continuamente as imagens enquanto a câmara estiver aberta.
    while cap.isOpened():
        start_time = time.time()

        # Lê uma imagem da câmara; termina se a captura falhar.
        if not success:
            print("Falha ao capturar imagem da câmera")
            break

        # Deteta a pose e obtém as coordenadas dos pontos corporais.
        lmList = detector.findPosition(img, draw=False)

        # Calcula e apresenta a taxa de imagens por segundo (FPS).
        fps = 1 / (cTime - pTime) if cTime - pTime > 0 else 0
        pTime = cTime
        cv2.putText(img, f'FPS: {int(fps)}', (10, 50),
                    cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 0), 2)

        # Regista os ângulos a cada intervalo definido, apenas se houver pontos detetados.
        if cTime - last_sample_time >= sampling_rate and len(lmList) != 0:
            # Calcula os ângulos da perna direita e da perna esquerda (anca, joelho e tornozelo).
            angle_right = round(findAngle(img, lmList[24], lmList[26], lmList[28]), 2)
            angle_left = round(findAngle(img, lmList[23], lmList[25], lmList[27]), 2)

            # Guarda o instante da amostra e os dois ângulos no ficheiro CSV.
            timestamp = round(cTime - start_video_time, 2)  # Tempo relativo ao início
            csv_writer.writerow([timestamp, angle_right, angle_left])
            last_sample_time = cTime

        cv2.imshow("MediaPipe Pose", img)

        # Espera o tempo restante para respeitar o limite de FPS definido.
        elapsed = time.time() - start_time
        if elapsed < frame_interval:
            time.sleep(frame_interval - elapsed)

        # Termina a captura quando a tecla 'q' é pressionada.
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Liberta a câmara e fecha o ficheiro e as janelas do OpenCV.
    cap.release()
    csv_file.close()
    cv2.destroyAllWindows()


# Executa a função principal apenas quando este ficheiro é corrido diretamente.
if __name__ == "__main__":
    main()