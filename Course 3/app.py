import pyhula
import time
from hula_video import hula_video
import cv2
import numpy as np
import threading
import math
from datetime import datetime

api = pyhula.UserApi()  

def detect_ball(frame, color):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    if color == "blue":
        lower = np.array([100, 150, 70])
        Upper = np.array([140, 255, 255])
        mask = cv2.inRange(hsv, lower, Upper)

    if color == "red":
        lower1 = np.array([0, 80, 70])
        Upper1 = np.array([15, 100, 100])
        mask1 = cv2.inRange(hsv, lower1, Upper1)

        lower2 = np.array([345, 95, 70])
        Upper2 = np.array([355, 100, 100])
        mask2 = cv2.inRange(hsv, lower2, Upper2)

        mask = cv2.bitwise_or(mask1, mask2)
    
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    if contours:
        largest_contour = max(contours, key=cv2.contourArea)
        x, y, w, h = cv2.boundingRect(largest_contour)
        center_x = x + w // 2
        center_y = y + h // 2
        
        cv2.drawContours(frame, [largest_contour], -1, (255, 0, 0), 3)  # Blue color
        cv2.circle(frame, (center_x, center_y), 5, (0, 255, 0), -1)  # Green dot at center
        
        return center_x, center_y, frame
    else:
        return None, None, frame

if not api.connect():
    print("Connection error")
else:
    print("Connection to station by WiFi")
    battery = api.get_battery()
    print("battery level: " + str(api.get_battery()))
    timestamp = datetime.now().strftime("%d-%b-%Y_%I-%M-%S%p")

    video = hula_video(api, display=False)
    video.video_mode_on()
    video.startrecording(filename=f"Outputs/OBS-3/Recording-{timestamp}")

    api.single_fly_takeoff()

    api.Plane_cmd_camera_angle(1, 45)

    while True:
        frame = video.get_video()
        x,y, frame = detect_ball(frame, "red")
        if x != None:
            print(f"Red Ball Detected at {x},{y}")
            cv2.imshow("Ball Detection", frame)
            cv2.imwrite(f"Outputs/OBS-3/Red-Detection-{timestamp}.png/", frame)
            cv2.waitKey(1)
            api.single_fly_curvilinearFlight(10, 40, -30)
            api.single_fly_turnleft(90)
            time.sleep(1)

            break
    
    while True:
        frame = video.get_video()
        x,y, frame = detect_ball(frame, "blue")
        if x != None:
            print(f"Blue Ball Detected at {x},{y}")
            cv2.imshow("Ball Detection", frame)
            cv2.imwrite(f"Outputs/OBS-3/Blue-Detection-{timestamp}.png/", frame)
            cv2.waitKey(1)
            api.single_fly_curvilinearFlight(-30, -20, 0)
            api.single_fly_forward(30)
            break
        

    cv2.destroyAllWindows()
    video.stoprecording()
    video.close()

    api.single_fly_touchdown()


