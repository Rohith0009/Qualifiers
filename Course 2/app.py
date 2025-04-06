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

move_complete = False
google_detect = False


def circle_up(radius, height_increase, num_steps, loops):
    while loop < loops:
        delta_theta = 2 * math.pi / num_steps
        z = height_increase / num_steps

        for i in range(num_steps):
            theta_i = i * delta_theta
            theta_next = (i + 1) * delta_theta

            x_i = radius * math.cos(theta_i)
            y_i = radius * math.sin(theta_i)
            x_next = radius * math.cos(theta_next)
            y_next = radius * math.sin(theta_next)

            dx = x_next - x_i
            dy = y_next - y_i

            turn = 360/num_steps

            api.single_fly_curvilinearFlight(dx, dy, z)
            api.single_fly_turnleft(turn)

            time.sleep(0.1)
        loop+=1

    move_complete = True

def detection():
    while not move_complete:
        frame = video.get_video()
        object_found, frame = detector.detect(frame)
        if not object_found is None:
            print(F"Found object: {object_found}")
        cv2.imshow("Detection", frame)
        cv2.imwrite(f"Outputs/OBS-2/Detection-{timestamp}.png/", frame)
        cv2.waitKey(1)
        time.sleep(0.1)


if not api.connect():
    print("Connection error")
else:
    print("Connection to station by WiFi")
    battery = api.get_battery()
    print("battery level: " + str(api.get_battery()))
    timestamp = datetime.now().strftime("%d-%b-%Y_%I-%M-%S%p")

    video = hula_video(hula_api=api,display=False)
    detector = tflite_detector(model="model.tflite",label="label.txt")
    video.video_mode_on()
    video.startrecording(filename=f"Outputs/OBS-2/Recording-{timestamp}")

    api.single_fly_takeoff()
    api.single_fly_forward(10)

    move = threading.Thread(target=circle_up, args=[50,30,100, 1])
    detect = threading.Thread(target=detection, args=[])
    move.start()
    detect.start()
    move.join()
    detect.join()

    cv2.destroyALLWindows()
    video.stoprecording()
    video.close()

    api.single_fly_up(20)
    api.single_fly_forward(10)
    api.single_fly_touchdown()
