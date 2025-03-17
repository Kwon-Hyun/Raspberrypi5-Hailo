#! 라즈베리파이 <> Picamera2를 통해 영상 출력 가능한 코드 (그 이전엔 웹캠만 가능이었음)
import cv2
import numpy as np
import pygame
from ultralytics import YOLO
from ultralytics.utils.checks import check_yaml
from ultralytics.utils import yaml_load
import time
import os
from picamera2 import Picamera2

# 사용할 YOLO model 불러오기
model = YOLO("model/yolov8n.pt")
CLASSES = yaml_load(check_yaml('coco128.yaml'))['names']
colors = np.random.uniform(0, 255, size=(len(CLASSES), 3))

# 오디오 설정
pygame.mixer.init()

# 카메라 초기화 (hailo 안 쓸 땐 Picamera2 // 쓸 땐 Gstreamer)
picam2 = Picamera2()
config = picam2.create_preview_configuration(main={"size": (1280, 720), "format": "RGB888"})
picam2.configure(config)
picam2.start()

# 사람 감지 여부 확인용 변수
# audio 재생 시간 파악을 위한 변수
last_play_time = 0  # 마지막으로 경고 tts가 재생된 시간

try:
    while True:
        try:
            frame = picam2.capture_array()
        
        except Exception as e:
            print(f"Frame Error.. : {e}")
        
        results = model(frame, stream=True)

        class_ids = []
        confidences = []
        bboxes = []
        person_detected = False  # human detection 여부 (감지 시, True)

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

        # B-Box 그리기
        font = cv2.FONT_HERSHEY_PLAIN
        for i in range(len(bboxes)):
            label = str(CLASSES[int(class_ids[i][0])])
            if label == 'person':
                if i in result_boxes:
                    person_detected = True  # Human Detection 성공.
                    bbox = list(map(int, bboxes[i])) 
                    x, y, x2, y2 = bbox
                    color = colors[i]
                    color = (int(color[0]), int(color[1]), int(color[2]))

                    cv2.rectangle(frame, (x, y), (x2, y2), color, 2)
                    cv2.putText(frame, label, (x, y - 10), font, 2, color, 2)

        # 사람 감지 & 최근 7초 이내에 주의 사운드가 재생되지 않았다면 재생되도록!
        current_time = time.time()
        if person_detected and (current_time - last_play_time > 7):
            pygame.mixer.music.load("audio/OHT-tts1.mp3")
            pygame.mixer.music.play()
            last_play_time = current_time  # 마지막 재생 시간 update

        # 화면 출력
        cv2.imshow("Human Detection and Sound", frame)

        # 종료 조건
        key = cv2.waitKey(1)
        if key & 0xFF == ord('q') or key == 27:
            break

finally:
    picam2.stop()
    cv2.destroyAllWindows()
    pygame.mixer.quit()
