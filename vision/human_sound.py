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

# 카메라 초기화
picam2 = Picamera2()
config = picam2.create_preview_configuration(main={"size": (1280, 720), "format": "RGB888"})
picam2.configure(config)
picam2.start()

# 사람 감지 여부 확인용 변수
last_play_time = 0  # 마지막으로 경고 TTS가 재생된 시간
text_file_path = "vision/humanDetect.txt"  # 이 파일이 0 또는 1로 업데이트됨

def read_signal():
    """ Reads the value from the text file (0 or 1). """
    try:
        with open(text_file_path, "r") as file:
            return file.read().strip()
    except Exception as e:
        print(f"Error reading signal file: {e}")
        return "0"  # 기본적으로 감지 안 한 것으로 가정

while True:
    frame = picam2.capture_array()
    
    results = model(frame, stream=True)

    class_ids = []
    confidences = []
    bboxes = []
    person_detected = False  # human detection 여부

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

    # 사람 감지 & 최근 7초 이내에 주의 사운드가 재생되지 않았으며, 파일이 1이면 재생
    current_time = time.time()
    amr_signal = read_signal()  # 파일 값 읽기

    if person_detected == True and amr_signal == "1" and (current_time - last_play_time > 7):
        pygame.mixer.music.load("audio/OHT-tts1.mp3")
        pygame.mixer.music.play()
        last_play_time = current_time  # 마지막 재생 시간 update

    # 화면 출력
    cv2.imshow("Human Detection and Sound", frame)

    key = cv2.waitKey(1)
    if key & 0xFF == ord('q') or key == 27:
        break

picam2.stop()
cv2.destroyAllWindows()
pygame.mixer.quit()
