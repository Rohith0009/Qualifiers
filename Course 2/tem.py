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

global loop, move_complete


move_complete = False
google_detect = False


def circle_up(radius, height_increase, num_steps, loops):
    global move_complete
    api.single_fly_radius_around(100)
    api.single_fly_up(30)
    api.single_fly_radius_around(100)
    move_complete=True

def detection():
    print("gergre")
    while not move_complete:
        frame = video.get_video()
        object_found, frame = detector.detect(frame)
        if not object_found is None:
            print(F"Found object: {object_found}")
            if object_found['label']=="Google":
                print("DETECTED!!!")
                cv2.imshow("Detection", frame)
                timestamp = datetime.now().strftime("%d-%b-%Y_%I-%M-%S%p")
                cv2.imwrite(f"photo{timestamp}.jpeg", frame)
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
    video.video_mode_on()
    video.startrecording(filename=f"2/Recording-{timestamp}.jpeg")

    api.single_fly_takeoff()
    api.single_fly_forward(10)

    move = threading.Thread(target=circle_up, args=[50,30,100, 1])
    detect = threading.Thread(target=detection, args=[])
    move.start()
    detect.start()
    move.join()
    detect.join()

    api.single_fly_up(20)
    api.single_fly_forward(10)
    api.single_fly_touchdown()
