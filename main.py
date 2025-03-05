from hailo_platform import PcieDevice, HEF, InferVStreams, InputVStreams, OutputVStreams
from pyzbar.pyzbar import decode
import cv2 as cv
import numpy as np

# QRcode 기준 pixel size
QR_SIZE = 0.06  # m
PIXEL_TO_MM = 0.264  # 예시 (1pixel = 0.264,,)

def detect_qr_with_hailo(image, results):
    data = "None"
    qr_center = None
    frame_center = None

    # Hailo 결과에서 박스 탐지 정보 처리
    for detection in results:
        x1, y1, x2, y2, confidence, class_id = detection
        x1, y1, x2, y2 = map(int, [x1, y1, x2, y2])

        qr_center = ((x1 + x2) // 2, (y1 + y2) // 2)
        frame_center = (image.shape[1] // 2, image.shape[0] // 2)

        center_distance_x = (qr_center[0] - frame_center[0]) * PIXEL_TO_MM
        center_distance_y = (qr_center[1] - frame_center[1]) * PIXEL_TO_MM

        cv.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)  # 바운딩 박스
        cv.circle(image, qr_center, 5, (0, 255, 255), -1)       # QR 중심

        # QR Decoding
        qr_roi = image[y1:y2, x1:x2]
        decoded_objects = decode(qr_roi)

        for obj in decoded_objects:
            data = obj.data.decode('utf-8')
            print(f"QR Decoded Data: {data}")

        # 화면에 정보 출력
        cv.putText(image, f"QR Center: {qr_center}", (10, 30), cv.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
        cv.putText(image, f"Distance: ({center_distance_x:.2f}, {center_distance_y:.2f}) mm", (10, 50),
                   cv.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)
    return image, qr_center, data

def main():
    # Hailo 장치 초기화
    device = PcieDevice()
    hef = HEF("model/hailo_best.hef")  # Hailo용 최적화된 모델
    vstreams_params = hef.create_vstreams_params(device)
    input_vstreams = InputVStreams(device, vstreams_params)
    output_vstreams = OutputVStreams(device, vstreams_params)

    # 카메라 초기화
    cap = cv.VideoCapture(0)
    if not cap.isOpened():
        print("카메라를 열 수 없습니다.")
        return

    while True:
        ret, frame = cap.read()
        if not ret:
            print("프레임을 읽을 수 없습니다.")
            break

        # 입력 프레임을 모델에 전달
        input_data = cv.resize(frame, (640, 640))  # 모델 입력 크기로 조정
        input_vstreams.write([input_data])

        # 모델 추론 결과 읽기
        output = output_vstreams.read()
        detections = output[0]  # YOLO 결과

        # QR 코드 탐지 및 시각화
        annotated_frame, qr_center, data = detect_qr_with_hailo(frame, detections)

        # 결과 출력
        cv.imshow('Hailo YOLOv8 QR Detection', annotated_frame)

        # 'q' 키를 누르면 종료
        if cv.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv.destroyAllWindows()

if __name__ == "__main__":
    main()