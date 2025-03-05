import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst, GLib
import os
import numpy as np
import cv2
import hailo
from hailo_rpi_common import (
    get_caps_from_pad,
    get_numpy_from_buffer,
    app_callback_class,
)
from detection_pipeline import GStreamerDetectionApp
import paho.mqtt.publish as publish


# -----------------------------------------------------------------------------------------------
# User-defined class to be used in the callback function
# -----------------------------------------------------------------------------------------------
# Inheritance from the app_callback_class
class user_app_callback_class(app_callback_class):
    def __init__(self):
        super().__init__()
        self.new_variable = 42  # New variable example


    def new_function(self):  # New function example
        return "The meaning of life is: "


def create_message(center_value):
    return {
        'ID': 'A',
        'Center': str(center_value),
        'Unit': 'cm'
    }

'''
mosquitto_pub/sub -h localhost -p 1883 -t camera/oht1 -m {”ID”: “A”,  “x1”: “100”, “y1”: “50”, “x2-x1”: “20”, “y2-y1”: “20”  }
'''


# -----------------------------------------------------------------------------------------------
# User-defined callback function
# -----------------------------------------------------------------------------------------------

# This is the callback function that will be called when data is available from the pipeline
def app_callback(pad, info, user_data):

    # Get the GstBuffer from the probe info
    buffer = info.get_buffer()
    # Check if the buffer is valid
    if buffer is None:
        return Gst.PadProbeReturn.OK

    # Using the user_data to count the number of frames
    user_data.increment()
    string_to_print = f"Frame count: {user_data.get_count()}\n"

    # Get the caps from the pad
    format, width, height = get_caps_from_pad(pad)

    print(f'LABEL{width}')

    # If the user_data.use_frame is set to True, we can get the video frame from the buffer
    frame = None
    if user_data.use_frame and format is not None and width is not None and height is not None:
        # Get video frame
        frame = get_numpy_from_buffer(buffer, format, width, height)

    # Get the detections from the buffer
    roi = hailo.get_roi_from_buffer(buffer)
    detections = roi.get_objects_typed(hailo.HAILO_DETECTION)



        # MQTT broker configuration
        # self.MQTT_BROKER = "localhost"
            # BROKER는 추후 192.xxx.xx.x 처럼 serverPC IP로 변경
        # self.MQTT_PORT = 1883
        # self.MQTT_TOPIC = "camera/oht1"

    # Parse the detections
    detection_count = 0
    for detection in detections:
        label = detection.get_label()
        bbox = detection.get_bbox()
        confidence = detection.get_confidence()


        if label == "person":
            string_to_print += f"Detection: {label} {confidence:.2f}\n"
            detection_count += 1
        
        if label == "QR code":

            x1_norm = bbox.xmin()
            y1_norm = bbox.ymin()
            x2_norm = bbox.xmax()
            y2_norm = bbox.ymax()
            x1 = int(x1_norm * width)
            y1 = int(y1_norm * height) # # # # 
            x2 = int(x2_norm * width)
            y2 = int(y2_norm * height)
            qr_detection = (x1, y1, x2 - x1, y2 - y1)
            print(qr_detection)


            message = create_message(y1)
        
            # # Publish the message
            # publish.single(
            #     topic="camera/oht1",
            #     payload=str(message),
            #     hostname="192.168.0.72",
            #     port=1883,
            # )

            string_to_print += f"Detection: {label} {confidence:.2f} \n"
            detection_count += 1
            
        
    if user_data.use_frame:
        # Note: using imshow will not work here, as the callback function is not running in the main thread
        # Let's print the detection count to the frame
        cv2.putText(frame, f"Detections: {detection_count}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        # Example of how to use the new_variable and new_function from the user_data
        # Let's print the new_variable and the result of the new_function to the frame
        cv2.putText(frame, f"{user_data.new_function()} {user_data.new_variable}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        # Convert the frame to BGR
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        user_data.set_frame(frame)

    print(string_to_print)
    return Gst.PadProbeReturn.OK

if __name__ == "__main__":
    # Create an instance of the user app callback class
    user_data = user_app_callback_class()
    app = GStreamerDetectionApp(app_callback, user_data)
    app.run()