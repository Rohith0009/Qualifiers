import pyhula
import time
from hula_video import hula_video
from tflite_detector import tflite_detector
import cv2
import threading
from datetime import datetime

api = pyhula.UserApi()

move_complete = False


def circle_up():
    global move_complete
    api.single_fly_radius_around(100)
    api.single_fly_up(30)
    api.single_fly_radius_around(100)
    move_complete=True

def detection():
    global final_detected
    while not move_complete:
        frame = video.get_video()
        object_found, frame = detector.detect(frame)
        if not object_found is None:
            print(F"Found object: {object_found}")
            if object_found['label']=="Google":
                print("DETECTED!!!")
                final_detected = frame
                cv2.imshow("Detection", frame)
                timestamp = datetime.now().strftime("%d-%b-%Y_%I-%M-%S%p")
                cv2.imwrite(f"google-detection-{timestamp}.jpeg", frame)
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
    detector = tflite_detector(model="model.tflite", label="label.txt")
    video.video_mode_on()

    api.single_fly_takeoff()
    api.single_fly_down(30)
    api.single_fly_forward(10)

    move = threading.Thread(target=circle_up, args=[])
    detect = threading.Thread(target=detection, args=[])
    move.start()
    detect.start()
    move.join()
    detect.join()

    api.single_fly_up(50)
    api.single_fly_forward(10)
    if not api.single_fly_Qrcode_align(0,0)['result']:
        api.single_fly_Qrcode_align(0,0)
    api.single_fly_touchdown()

    cv2.imshow("Detection", final_detected)
    cv2.waitKey(100)
