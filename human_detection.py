import cv2
import numpy as np
from ultralytics import YOLO
from ultralytics.utils.checks import check_yaml
from ultralytics.utils import ROOT, yaml_load

# parameters
WIDTH = 1280
HEIGHT = 720
model = YOLO('model\yolov8n.pt')

CLASSES = yaml_load(check_yaml('coco128.yaml'))['names']
colors = np.random.uniform(0, 255, size=(len(CLASSES), 3))

# 웹캠 사용
cap = cv2.VideoCapture(0)  # 0번 카메라 (기본 웹캠)
cap.set(3, WIDTH)  # 가로 크기 설정
cap.set(4, HEIGHT)  # 세로 크기 설정

# Streaming loop
try:
    while True:
        ret, frame = cap.read()
        if not ret:
            print("webcam에서 프레임을 가져올 수 없습니다.")
            break

        # YOLO 모델 실행
        results = model(frame, stream=True)

        class_ids = []
        confidences = []
        bboxes = []
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
            if label == 'person':  # 사람만 감지
                if i in result_boxes:
                    bbox = list(map(int, bboxes[i])) 
                    x, y, x2, y2 = bbox
                    color = colors[i]
                    color = (int(color[0]), int(color[1]), int(color[2]))

                    cv2.rectangle(frame, (x, y), (x2, y2), color, 2)
                    cv2.putText(frame, label, (x, y - 10), font, 2, color, 2)

        cv2.imshow("Human Detection Test", frame)

        key = cv2.waitKey(1)
        if key & 0xFF == ord('q') or key == 27:
            break
finally:
    cap.release()
    cv2.destroyAllWindows()