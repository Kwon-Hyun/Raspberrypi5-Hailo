import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst, GLib
import hailo
import cv2
import pygame
import time
import os

from hailo_apps_infra.hailo_rpi_common import get_caps_from_pad, get_numpy_from_buffer
from hailo_apps_infra.detection_pipeline import GStreamerDetectionApp

# Hailo 모델 로드 (.hef 파일)
hef_path = "model/yolov8n.hef"  # 변환된 Hailo 모델 경로 (저장된 파일경로 확인 후 수정)

# 오디오 설정
mp3_path = os.path.join("audio/OHT-tts1.mp3")   # 생성한 tts audio 경로 (저장된 파일경로 확인 후 수정)
pygame.mixer.init()

# 카메라 pipeline 설정 (GStreamer 사용)
# pipeline 설정하는 부분은 오류 시, format 등 구글링 통해 수정 봐야 함.
GST_PIPELINE = "libcamera-vid ! video/x-raw, format=RGB, width=1280, height=720 ! videoconvert ! appsink"
cap = cv2.VideoCapture(GST_PIPELINE, cv2.CAP_GSTREAMER)


# cam 화면 출력 안될 때 확인용 코드
if not cap.isOpened():
    print("카메라를 열 수 없습니다.")
    exit()

# 사람 감지 여부 확인용 변수
# audio 재생 시간 파악을 위한 변수
last_play_time = 0  # 마지막으로 경고 tts가 재생된 시간

# callback 함수 정의
def app_callback(pad, info, user_data):
    buffer = info.get_buffer()
    if buffer is None:
        return Gst.PadProbeReturn.OK

    # 비디오 프레임 가져오기
    format, width, height = get_caps_from_pad(pad)
    frame = get_numpy_from_buffer(buffer, format, width, height)

    # Hailo 모델로 추론 실행
    roi = hailo.get_roi_from_buffer(buffer)
    detections = roi.get_objects_typed(hailo.HAILO_DETECTION)

    # 사람 감지 시, True 조건으로 변경하기 위한 변수
    person_detected = False

    for detection in detections:
        label = detection.get_label()
        confidence = detection.get_confidence()
        if label == "person" and confidence > 0.5:  # 0번 class == 'person'
            # 사람 감지 시, True
            person_detected = True

            # detection한 사람에 대해 bounding-box 그리기
            bbox = detection.get_bbox()
            x, y, x2, y2 = map(int, bbox)
            cv2.rectangle(frame, (x, y), (x2, y2), (0, 255, 0), 2)
            cv2.putText(frame, "person", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)


    # 사람이 감지되었고, 최근 7초 이내에 음악이 재생되지 않았다면 오디오 실행
    # 시간 설정은 detection 속도나 상황에 따라 조정해도 괜찮음.
    current_time = time.time()
    if person_detected and (current_time - last_play_time > 7):
        # 조건 성립하면 오디오 불러오고 재생
        pygame.mixer.music.load(mp3_path)
        pygame.mixer.music.play()
        last_play_time = current_time   # 마지막 재생시간 업데이트 위해 갱신

    # 화면 출력
    cv2.imshow("Human Detection", frame)
    
    return Gst.PadProbeReturn.OK

if __name__ == "__main__":
    # GStreamerDetectionApp 인스턴스 생성
    user_data = object()  # 사용자 정의 데이터 (콜백에 전달)
    app = GStreamerDetectionApp(app_callback, user_data)
    app.run()