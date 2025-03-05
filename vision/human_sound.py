import cv2
import numpy as np
import pygame
from ultralytics import YOLO
from ultralytics.utils.checks import check_yaml
from ultralytics.utils import yaml_load
import time

# parameters
WIDTH = 1280
HEIGHT = 720
model = YOLO('model/yolov8n.pt')
CLASSES = yaml_load(check_yaml('coco128.yaml'))['names']
colors = np.random.uniform(0, 255, size=(len(CLASSES), 3))

# 오디오 설정 (MP3 파일 상대경로 지정)
MP3_FILE = "audio/alert-ex.mp3"  # 사용할 MP3 파일 이름
pygame.mixer.init()

# 웹캠 사용
cap = cv2.VideoCapture(0)  # 0번 카메라 (기본 웹캠)
cap.set(3, WIDTH)
cap.set(4, HEIGHT)

# 사람 감지 여부 확인용 변수
last_play_time = 0  # 마지막으로 음악을 재생한 시간

# Streaming loop
try:
    while True:
        ret, frame = cap.read()
        if not ret:
            print("웹캠에서 프레임을 가져올 수 없습니다.")
            break

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
            pygame.mixer.music.load(MP3_FILE)  # MP3 파일 로드
            pygame.mixer.music.play()  # 부저 sound 재생
            last_play_time = current_time  # 마지막 재생 시간 업데이트

        cv2.imshow("Human Sound Test", frame)

        key = cv2.waitKey(1)
        if key & 0xFF == ord('q') or key == 27:
            break
finally:
    cap.release()
    cv2.destroyAllWindows()
    pygame.mixer.quit()  # pygame 종료