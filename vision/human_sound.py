import cv2
import numpy as np
import pygame
from ultralytics import YOLO
from ultralytics.utils.checks import check_yaml
from ultralytics.utils import yaml_load
import time
import os
from picamera2 import Picamera2

# 모델 및 오디오 파일 경로 설정
model_path = os.path.join("model/yolov8n.pt")
mp3_path = os.path.join("audio/OHT-tts1.mp3")

# YOLO 모델 로드
model = YOLO(model_path)
CLASSES = yaml_load(check_yaml('coco128.yaml'))['names']
colors = np.random.uniform(0, 255, size=(len(CLASSES), 3))

# 오디오 설정
pygame.mixer.init()

# 카메라 초기화
picam2 = Picamera2()
config = picam2.create_preview_configuration(main={"size": (1280, 720), "format": "RGB888"})
picam2.configure(config)
picam2.start()

# 사람 감지 여부 확인용 변수
last_play_time = 0  # 마지막으로 음악을 재생한 시간

try:
    while True:
        # Picamera2에서 프레임 가져오기
        try:
            frame = picam2.capture_array()
            
        except Exception as e:
            print(f"Frame Error.. : {e}")
        
        # YOLO 모델 실행
        results = model(frame, stream=True)

        class_ids = []
        confidences = []
        bboxes = []
        person_detected = False  # 사람 감지 여부

        for result in results:
            boxes = result.boxes
            for box in boxes:
                confidence = box.conf
                if confidence > 0.5:
                    xyxy = box.xyxy.tolist()[0]
                    bboxes.append(xyxy)
                    confidences.append(float(confidence))
                    class_ids.append(box.cls.tolist())

        result_boxes = cv2.dnn.NMSBoxes(bboxes, confidences, 0.25, 0.45, 0.5)

        # Bounding Box 그리기
        font = cv2.FONT_HERSHEY_PLAIN
        for i in range(len(bboxes)):
            label = str(CLASSES[int(class_ids[i][0])])
            if label == 'person':  # 사람 감지 시
                if i in result_boxes:
                    person_detected = True  # 사람 감지됨
                    bbox = list(map(int, bboxes[i])) 
                    x, y, x2, y2 = bbox
                    color = colors[i]
                    color = (int(color[0]), int(color[1]), int(color[2]))

                    cv2.rectangle(frame, (x, y), (x2, y2), color, 2)
                    cv2.putText(frame, label, (x, y - 10), font, 2, color, 2)

        # 사람이 감지되었고, 최근 7초 이내에 음악이 재생되지 않았다면 실행
        current_time = time.time()
        if person_detected and (current_time - last_play_time > 7):
            pygame.mixer.music.load(mp3_path)  # MP3 파일 로드
            pygame.mixer.music.play()  # 부저 sound 재생
            last_play_time = current_time  # 마지막 재생 시간 업데이트

        # 화면 출력
        cv2.imshow("Human Detection", frame)

        # 종료 조건
        key = cv2.waitKey(1)
        if key & 0xFF == ord('q') or key == 27:
            break

finally:
    picam2.stop()
    cv2.destroyAllWindows()
    pygame.mixer.quit()  # pygame 종료
