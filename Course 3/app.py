import pyhula
import time
from hula_video import hula_video
import cv2
import numpy as np
from datetime import datetime

api = pyhula.UserApi()  

req_area = 5000

alligned = False
x_complete = False
y_complete = False

def detect_ball(frame, color):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    if color == "blue":
        lower = np.array([100, 100, 100])
        Upper = np.array([130, 255, 255])
        mask = cv2.inRange(hsv, lower, Upper)

    if color == "red":
        lower1 = np.array([0, 120, 70])
        Upper1 = np.array([10, 255, 255])
        mask1 = cv2.inRange(hsv, lower1, Upper1)

        lower2 = np.array([170, 120, 70])
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
        
        return center_x, center_y, frame, area
    else:
        return None, None, frame, None

def move():
    api.single_fly_down(40)
    api.single_fly_forward(120)
    time.sleep(1)
    api.single_fly_back(120)

def detect_allign(color):
    global x_complete, y_complete
    alligned = False
    while not alligned:
        frame = video.get_video()
        x,y, frame, area = detect_ball(frame, color)
        if x != None  and area>=req_area :
            print(f"{color} Ball Detected at {x},{y}")
            cv2.imshow(f"{color} Detection", frame)
            cv2.waitKey(1)
            if x < 610:
                print("Moving Left")
                api.single_fly_left(20)
            elif x > 670:
                print("Moving Right")
                api.single_fly_right(20)

            else:
                x_complete = True
            if y > 390:
                print("Moving Forward")
                api.single_fly_back(20)        
            elif y < 320:
                print("moving Back")
                api.single_fly_forward(20)
            else:
                y_complete = True

            if x_complete and y_complete:
                print("Successfully alligned")
                alligned = True
                move()

if not api.connect():
    print("Connection error")
else:
    print("Connection to station by WiFi")
    battery = api.get_battery()
    print("battery level: " + str(api.get_battery()))

    timestamp = datetime.now().strftime("%d-%b-%Y_%I-%M-%S%p")

    video = hula_video(api, display=False)
    video.video_mode_on()

    api.single_fly_takeoff()
    api.single_fly_forward(70)
    api.Plane_cmd_camera_angle(1, 0)

    while True:
        frame = video.get_video()
        x,y, frame, area = detect_ball(frame, "blue")
        if x != None  and area>=req_area :
            print(f"Blue Ball Detected at {x},{y}")
            cv2.imshow(f"Blue Detection", frame)
            cv2.imwrite(f"Blue-Detection-{timestamp}.jpeg", frame)
            cv2.waitKey(1)
            break    

    while True:
        frame = video.get_video()
        x,y, frame, area = detect_ball(frame, "red")
        if x != None  and area>=req_area :
            print(f"Blue Red Detected at {x},{y}")
            cv2.imshow(f"Red Detection", frame)
            cv2.imwrite(f"Red-Detection-{timestamp}.jpeg", frame)
            cv2.waitKey(1)
            break    

    detect_allign("red")

    detect_allign("blue")

    cv2.destroyAllWindows()
    video.close()

    api.single_fly_touchdown()


