import pyhula
import time
from hula_video import hula_video
from tflite_detector import tflite_detector
import cv2
import numpy as np
import threading
import math
from datetime import datetime

api = pyhula.UserApi()

def detection():
    while True:
        frame = video.get_video()
        object_found, frame = detector.detect(frame)
        if not object_found is None:
            print(F"Found object: {object_found}, by Model: 1")
        cv2.waitKey(1)
        time.sleep(0.1)

def detection2():
    while True:
        frame = video.get_video()
        object_found, frame = detector2.detect(frame)
        if object_found is not None:
            print(f"Found object: {object_found}, by Model: 2")
        cv2.waitKey(1)
        time.sleep(0.1)

def detection3():
    while True:
        frame = video.get_video()
        object_found, frame = detector3.detect(frame)
        if object_found is not None:
            print(f"Found object: {object_found}, by Model: 3")
        cv2.waitKey(1)
        time.sleep(0.1)

def detection4():
    while True:
        frame = video.get_video()
        object_found, frame = detector4.detect(frame)
        if object_found is not None:
            print(f"Found object: {object_found}, by Model: 4")
        cv2.waitKey(1)
        time.sleep(0.1)

def detection5():
    while True:
        frame = video.get_video()
        object_found, frame = detector5.detect(frame)
        if object_found is not None:  
            print(f"Found object: {object_found}, by Model: 5")
        cv2.waitKey(1)
        time.sleep(0.1)


if not api.connect():
    print("Connection error")
else:
    print("Connection to station by WiFi")
    battery = api.get_battery()
    print("battery level: " + str(api.get_battery()))
    timestamp = datetime.now().strftime("%d-%b-%Y_%I-%M-%S%p")

    video = hula_video(hula_api=api,display=True)
    detector = tflite_detector(model="model.tflite", label="label.txt")
    detector2 = tflite_detector(model="model2.tflite", label="label.txt")
    detector3 = tflite_detector(model="model3.tflite", label="label.txt")
    detector4 = tflite_detector(model="model4.tflite", label="label.txt")
    detector5 = tflite_detector(model="model5.tflite", label="label.txt")
    video.video_mode_on()
    video.startrecording(filename=f"2/Recording-{timestamp}.jpeg")

    api.single_fly_takeoff()
    api.Plane_cmd_camera_angle(1, 90)

    detect = threading.Thread(target=detection, args=[])
    detect.start()
    detect2 = threading.Thread(target=detection2, args=[])
    detect2.start()
    detect3 = threading.Thread(target=detection3, args=[])
    detect3.start()
    detect4 = threading.Thread(target=detection4, args=[])
    detect4.start()
    detect5 = threading.Thread(target=detection5, args=[])
    detect5.start()

    detect.join()
    

    api.single_fly_touchdown()
