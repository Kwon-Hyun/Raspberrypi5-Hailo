<<<<<<< HEAD
import smbus
import math
import time
import numpy as np
import matplotlib.pyplot as plt
from simple_pid import PID
import paho.mqtt.client as mqtt
import json

# MQTT 설정
broker = "your_mqtt_broker_address"  # 브로커 주소
port = 1883  # MQTT 포트
topic = "your_topic"  # 구독할 주제

# MQTT 클라이언트 초기화
client = mqtt.Client()
client.connect(broker, port, 60)

# I2C 버스 설정
bus = smbus.SMBus(1)
ADXL345_ADDR = 0x53

# ADXL345 초기화
bus.write_byte_data(ADXL345_ADDR, 0x2D, 0x08)

# PID 파라미터
Kp = 1.2
Ki = 0.1
Kd = 0.05

# PID 변수 초기화
setpoint = 0.0
previous_error = 0.0
integral = 0.0

# PID 설정
pid = PID(Kp, Ki, Kd, setpoint=0)
pid.output_limits = (-100, 100)

# 실시간 그래프 설정
plt.ion()
fig, axs = plt.subplots(2, 1, figsize=(10, 5))

time_steps = []
y_values = []
control_signals = []
max_points = 100

def read_accel():
    data = bus.read_i2c_block_data(ADXL345_ADDR, 0x32, 6)
    
    x = (data[1] << 8) | data[0]
    y = (data[3] << 8) | data[2]
    z = (data[5] << 8) | data[4]

    if x & (1 << 15): x -= (1 << 16)
    if y & (1 << 15): y -= (1 << 16)
    if z & (1 << 15): z -= (1 << 16)

    x_g = x * 0.004 * 9.81
    y_g = y * 0.004 * 9.81
    z_g = z * 0.004 * 9.81

    return x_g, y_g, z_g

def calculate_tilt(x, y, z):
    angle_x = math.atan2(x, math.sqrt(y**2 + z**2)) * 180 / math.pi
    angle_y = math.atan2(y, math.sqrt(x**2 + z**2)) * 180 / math.pi
    return angle_x, angle_y

def pid_visualize(integral, previous_error):
    for t in range(500):
        x, y, z = read_accel()
        angle_x, angle_y = calculate_tilt(x, y, z)

        control_signal = pid(angle_y)

        error = setpoint - angle_x
        integral += error
        derivative = error - previous_error
        output = Kp * error + Ki * integral + Kd * derivative

        if len(time_steps) > max_points:
            time_steps.pop(0)
            y_values.pop(0)
            control_signals.pop(0)

        time_steps.append(t)
        y_values.append(angle_y)
        control_signals.append(control_signal)

        print(f"X: {x:.2f}, Y: {y:.2f}, Z: {z:.2f}")
        print(f"X-Angle: {angle_x:.2f}, Y-Angle: {angle_y:.2f}")
        print(f"PID Output: {output:.2f}")

        previous_error = error

        # MQTT로 데이터 전송
        data = {
            "x": x,
            "y": y,
            "z": z,
            "x_angle": angle_x,
            "y_angle": angle_y,
            "PID_output": output
        }
        client.publish(topic, json.dumps(data))

        axs[0].clear()
        axs[0].plot(time_steps, y_values, label="Y tilt")
        axs[0].axhline(0, color='red', linestyle="--", label="Target (0°)")
        axs[0].set_xlabel("Time Steps")
        axs[0].set_ylabel("Tilt")
        axs[0].legend()
        axs[0].set_title("angle_y degree - PID Control")

        axs[1].clear()
        axs[1].plot(time_steps, control_signals, label="PID Output", color="green")
        axs[1].set_xlabel("Time Steps")
        axs[1].set_ylabel("Control Signal")
        axs[1].legend()
        axs[1].set_title("PID Control Result")

        plt.pause(0.01)
        time.sleep(0.1)

    plt.ioff()
    plt.show()

    return x, y, z, angle_x, angle_y, output

pid_visualize(integral, previous_error)

# MQTT 클라이언트 연결 종료
client.disconnect()
=======
# 엄밀히는 mqtt 통신 아니고 그냥 json 파일로 저장해서 갱신 후 불러오는 형식으로 진행

import smbus
import math
import time
import numpy as np
import matplotlib.pyplot as plt
from simple_pid import PID
import paho.mqtt.client as mqtt
import json
import os

#! 초기화 및 설정
# 1. MQTT 통신 설정

# MQTT 설정
broker = "192.168.0.24"  # 혼자선 localhost테스트하기
port = 1883  # MQTT 포트
topic = "OHT/PID"

json_file = "PIDcontrol.json"
# JSON 파일이 없으면 생성
if not os.path.exists(json_file):
    with open(json_file, "w") as f:
        f.write("")  # 빈 json 파일로 초기화

# MQTT 클라이언트 초기화
client = mqtt.Client()
client.connect(broker, port, 60)


# 2. 보드 <> 센서 설정
# I2C 버스 설정
bus = smbus.SMBus(1)
ADXL345_ADDR = 0x53

# ADXL345 초기화
bus.write_byte_data(ADXL345_ADDR, 0x2D, 0x08)

#! 계속 test 해봐야 하는 부분
# PID 파라미터 (Kp, Ki, Kd) (test를 통해 계속 수정해서 최적값 찾아야함..ㅠㅠ)
Kp = 1.2  # 비례 gain
Ki = 0.1  # 적분 gain
Kd = 0.05 # 미분 gain

# PID 변수 초기화
setpoint = 0.0  # 목표 기울기 (0도 (움직이지 않고 평평한 상태로..))
previous_error = 0.0
integral = 0.0

# PID 설정 (목표 : x축 또는 y축 기울기를 0°로 보정)
pid = PID(Kp, Ki, Kd, setpoint=0)
pid.output_limits = (-100, 100)  # 보정 가능한 범위 제한

#! 시각화 및 터미널 출력
# 실시간 그래프 설정
plt.ion()
fig, axs = plt.subplots(2, 1, figsize=(10, 5))

time_steps = []
y_values = []
control_signals = []
max_points = 100    # 그래프에 표시할 최대 데이터 개수



#! ADXL345 실제 값들 받아오기
# 가속도 센서 데이터 읽기
def read_accel():
    data = bus.read_i2c_block_data(ADXL345_ADDR, 0x32, 6)
    
    x = (data[1] << 8) | data[0]
    y = (data[3] << 8) | data[2]
    z = (data[5] << 8) | data[4]

    if x & (1 << 15): x -= (1 << 16)
    if y & (1 << 15): y -= (1 << 16)
    if z & (1 << 15): z -= (1 << 16)

    x_g = x * 0.004 * 9.81
    y_g = y * 0.004 * 9.81
    z_g = z * 0.004 * 9.81

    return x_g, y_g, z_g

# 기울기(각도) 계산 함수
def calculate_tilt(x, y, z):
    angle_x = math.atan2(x, math.sqrt(y**2 + z**2)) * 180 / math.pi
    angle_y = math.atan2(y, math.sqrt(x**2 + z**2)) * 180 / math.pi
    return angle_x, angle_y

# PID 계산 및 시각화 함수
def pid_visualize(integral, previous_error):
    for t in range(500):
        x, y, z = read_accel()
        angle_x, angle_y = calculate_tilt(x, y, z)

        control_signal = pid(angle_y)

        # PID 제어 계산
        error = setpoint - angle_x  # 목표 각도(0도) - 센서에서 측정된 실제 각도 간 오차
        integral += error   # 전체 적분값 : integral += 제어주기*error * Ki
        derivative = error - previous_error
        output = Kp * error + Ki * integral + Kd * derivative

        # 데이터 저장 (최대 데이터 개수 유지)
        if len(time_steps) > max_points:
            time_steps.pop(0)
            y_values.pop(0)
            control_signals.pop(0)

        time_steps.append(t)
        y_values.append(angle_y)
        control_signals.append(control_signal)

        print(f"X: {x:.2f}, Y: {y:.2f}, Z: {z:.2f}")
        print(f"X-Angle: {angle_x:.2f}, Y-Angle: {angle_y:.2f}")
        print(f"PID Output: {output:.2f}")

        previous_error = error  # 실시간으로 오차 업데이트 하기 위함.

        # MQTT로 데이터 전송
        data = {
            "x": f"{x:.2f}",
            "y": f"{y:.2f}",
            "z": f"{z:.2f}",
            "x_angle": f"{angle_x:.2f}",
            "y_angle": f"{angle_y:.2f}",
            "PID_output": f"{output:.2f}"
        }
        client.publish(topic, json.dumps(data))

        # 초기에 지정한 json 파일에 데이터 저장
        with open(json_file, "w") as f: # 계속 덮어쓰기해주는 형식
            json.dump(data, f)
            #f.write("\n")  # 각 데이터 항목을 새 줄에 저장 no갱신

        axs[0].clear()
        axs[0].plot(time_steps, y_values, label="Y tilt")
        axs[0].axhline(0, color='red', linestyle="--", label="Target (0°)")
        axs[0].set_xlabel("Time Steps")
        axs[0].set_ylabel("Tilt")
        axs[0].legend()
        axs[0].set_title("angle_y degree - PID Control")

        axs[1].clear()
        axs[1].plot(time_steps, control_signals, label="PID Output", color="green")
        axs[1].set_xlabel("Time Steps")
        axs[1].set_ylabel("Control Signal")
        axs[1].legend()
        axs[1].set_title("PID Control Result")

        plt.pause(0.01)
        time.sleep(0.1)

    plt.ioff()
    plt.show()

    return x, y, z, angle_x, angle_y, output

pid_visualize(integral, previous_error)

# MQTT 클라이언트 연결 종료
client.disconnect()
>>>>>>> 2da5b1cf3c5689d401b6ef65a869c47c8328a5d9
