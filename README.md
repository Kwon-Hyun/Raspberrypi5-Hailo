# Raspberrypi5-Hailo
Live Streaming and detect QR, centering with Raspberrypi5 &amp; Hailo Ai kit

---
### Project
project/<br>
├── audio<br>
&emsp;      ├── alert-ex.mp3<br>
&emsp;      ├── OHT-tts1.mp3<br>
├── model<br>
&emsp;      ├── best.onnx ( .pt -> .onnx -> .hef 로 변환해야 Hailo에서 사용 가능 )<br>
&emsp;      ├── best.pt ( for QR detection )<br>
&emsp;      ├── yolov8n.pt ( for human detection , file name : vision/human_sound.py )<br>
&emsp;      ├── yolov8n.hef ( for human detection with HailoAI )<br>
&emsp;      ├── yolov8n.zip ( public yolov8 models zip file ; .pt, .hef )<br>
&emsp;      ├── convert.ipynb ( for HailoAI ; 적용을 위해 model 확장자 변경 위한 ipynb )<br>
├── mqtt  ( just for mqtt test )<br>
&emsp;      ├── mqttqr.py<br>
&emsp;      ├── pid_mqtt.py<br>
├── sensor<br>
&emsp;      ├── adxl_pid.py<br>
&emsp;      ├── adxl.py<br>
├── test<br>
&emsp;      ├── qr_create.py ( QR code image 생성용 source code )<br>
&emsp;      ├── sound_test.py<br>
&emsp;      ├── test_picam.py<br>
├── vision<br>
&emsp;      ├── human_detection.py<br>
&emsp;      ├── human_sound_hailo.py<br>
&emsp;      ├── human_sound.py<br>
└── .gitignore<br>
└── main.py<br>
└── README.md<br>

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
best.pt ( for QR barcode ; 약 1072장의 이미지들로 학습 진행한 model by roboflow )
<br><br>
:: dataset 정보 ::
<br>
&emsp; Dataset Split : train 989장, valid 82장, test 0장
<br>
&emsp; 전처리 : auto-oriented:Applied, Resize:Stretch to 2048x2048
<br>
&emsp; Augmentations : Outputs per training example:3, Brightness:Between -10% ~ +10%, Exposure:Between -10% ~ +10%
<br>
<br>
<b>2. Hailo</b>
sudo apt update && sudo apt full-upgrade
<br>
sudo raspi-config ( "6 Advanced Options" > "A8 PCIe Speed": "Yes" > "Finish" )
<br>
sudo reboot
<br>
sudo apt install hailo-all
<br>
sudo reboot
<br>
hailortcli fw-control identify
<br>
<br>
<b>3. Library</b>

- hailo-apps-infra
<br>
pip install git+https://github.com/hailo-ai/hailo-apps-infra.git
<br>
(Download link : https://github.com/hailo-ai/hailo-apps-infra)
<br>

- Picamera2
<br>
pip install picamera2
