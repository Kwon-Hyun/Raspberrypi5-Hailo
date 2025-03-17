# Raspberrypi5-Hailo
Live Streaming and detect QR, centering with Raspberrypi5 &amp; Hailo Ai kit

---
### Project
project/
├── audio
      ├── alert-ex.mp3
      ├── OHT-tts1.mp3
├── model
      ├── best.onnx ( .pt -> .onnx -> .hef 로 변환해야 Hailo에서 사용 가능 )
      ├── best.pt ( for QR detection )
      ├── yolov8n.pt ( for human detection , file name : vision/human_sound.py )
      ├── yolov8n.hef ( for human detection with HailoAI )
      ├── yolov8n.zip ( public yolov8 models zip file ; .pt, .hef )
      ├── convert.ipynb ( for HailoAI ; 적용을 위해 model 확장자 변경 위한 ipynb )
├── mqtt  ( just for mqtt test )
      ├── mqttqr.py
      ├── pid_mqtt.py
├── sensor
      ├── adxl_pid.py
      ├── adxl.py
├── test
      ├── qr_create.py ( QR code image 생성용 source code )
      ├── sound_test.py
      ├── test_picam.py
├── vision
      ├── human_detection.py
      ├── human_sound.py
└── .gitignore
└── main.py
└── README.md

---
### Installation

<b>1. Model</b>

- Public Pretrained Models
<br>
YOLOv8n.hef for Hailo
<br>
(Download link : https://github.com/hailo-ai/hailo_model_zoo/blob/db0d735604d4b1f2d5ed1bdfa527a7fd1ad192c2/docs/public_models/HAILO8/HAILO8_object_detection.rst#L629)

<br>
- Trained Models
<br>
best.pt ( for QR barcode ; 약 1072장의 이미지들로 학습 진행한 model )
