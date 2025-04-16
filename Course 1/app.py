import pyhula
import time
from hula_video import hula_video
from tflite_detector import tflite_detector
import cv2
from datetime import datetime
import threading
import numpy as np


api = pyhula.UserApi()

blue_height = []
red_height = []

def detect_ball(frame, color):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    if color == "blue":
        lower = np.array([100, 100, 100])
        Upper = np.array([130, 255, 255])
        mask = cv2.inRange(hsv, lower, Upper)

    if color == "red":
        lower1 = np.array([0, 150, 150])
        Upper1 = np.array([10, 255, 255])
        mask1 = cv2.inRange(hsv, lower1, Upper1)

        lower2 = np.array([170, 150, 150])
        Upper2 = np.array([180, 255, 255])
        mask2 = cv2.inRange(hsv, lower2, Upper2)

        mask = cv2.bitwise_or(mask1, mask2)
    
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    if contours:
        largest_contour = max(contours, key=cv2.contourArea)
        x, y, w, h = cv2.boundingRect(largest_contour)
        area = cv2.contourArea(largest_contour)
        print(area)
        center_x = x + w // 2
        center_y = y + h // 2
        if color == "blue":
            cv2.drawContours(frame, [largest_contour], -1, (255, 0, 0), 3)  # Blue color
        elif color == "red":
            cv2.drawContours(frame, [largest_contour], -1, (0, 0, 255), 3)  # Red color
        cv2.circle(frame, (center_x, center_y), 5, (0, 255, 0), -1)  # Green dot at center
        
        blue_height.append(tof0 - api.get_plane_distance())
            
        #if rgb["state"]==True and result == "red":
        #    red_height.append(tof0 - api.get_plane_distance())

        api.single_fly_forward(20)

        return center_x, center_y, frame, area
    else:
        return None, None, frame, None



imda_detect = False

if not api.connect():
    print("Connection error")
else:
    print("Connection to station by WiFi")
    battery = api.get_battery()
    print("battery level: " + str(api.get_battery()))
    timestamp = datetime.now().strftime("%d-%b-%Y_%I-%M-%S%p")

    video = hula_video(hula_api=api,display=False)
    detector = tflite_detector(model="model.tflite", label="label.txt")
    video.video_mode_on()


    api.single_fly_takeoff()
    api.Plane_cmd_camera_angle(1,90)
    time.sleep(1)
    tof0 = api.get_plane_distance()

    api.single_fly_forward(90)

    time.sleep(1)

    tof1 = api.get_plane_distance()
    print(f"Height of 1'st Step: {tof0-tof1}")
    api.single_fly_forward(60)

    time.sleep(1)
    tof2 = api.get_plane_distance()
    print(f"Height of 2'nd Step: {tof0-tof2}")
    api.single_fly_forward(60)

    while not imda_detect:    
        print("attempting")
        frame = video.get_video()
        object_found, frame = detector.detect(frame)
        if not object_found is None:
            print(F"Found object: {object_found}")
            if object_found['label']=="IMDA":
                print("DETECTED!!!")
                final_frame = frame
                cv2.imshow("Detection", frame)
                cv2.imwrite(f"IMDA-detection-{timestamp}.jpeg", frame)
                imda_detect = True
                break
        cv2.waitKey(1)
        time.sleep(0.1)

    api.single_fly_touchdown()

    cv2.imshow("Detection", final_frame)
    cv2.waitKey(100)

print(blue_height)
print(red_height)


    