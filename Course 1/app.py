import pyhula
import time
from hula_video import hula_video
from tflite_detector import tflite_detector
import cv2
import numpy as np
import threading
import math

api = pyhula.UserApi()

imda_detect = False

if not api.connect():
    print("Connection error")
else:
    print("Connection to station by WiFi")
    battery = api.get_battery()
    print("battery level: " + str(api.get_battery()))

    video = hula_video(hula_api=api,display=False)
    detector = tflite_detector(model="model.tflite",label="label.txt")
    video.video_mode_on()
    video.startrecording()

    api.single_fly_takeoff()
    api.Plane_cmd_camera_angle(1,90)
    tof0 = api.get_plane_distance()
    api.single_fly_forward(30)

    tof1 = api.get_plane_distance()
    print(f"Height of 1'st Step: {tof0-tof1}")
    api.single_fly_forward(30)
    tof2 = api.get_plane_distance()
    print(f"Height of 2'nd Step: {tof0-tof2}")

    while not imda_detect:    
        frame = video.get_video()
        object_found, frame = detector.detect(frame)
        if not object_found is None:
            print(F"Found object: {object_found}")
            if object_found=="IMDA":
                imda_detect = True
        cv2.imshow("Detection", frame)
        api.Plane_fly_take_photo()
        cv2.waitKey(1)
        time.sleep(0.1)
        break
    cv2.destroyAllWindows()
    video.stoprecording()
    video.close()

    api.single_fly_touchdown()


    