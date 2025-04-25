import pyhula
import time
from hula_video import hula_video
from tflite_detector import tflite_detector
import cv2
from datetime import datetime



api = pyhula.UserApi()

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

    api.single_fly_forward(100)


    tof1 = api.get_plane_distance()
    print(f"Height of 1'st Step: {tof0-tof1}")

    time.sleep(1)

    api.single_fly_forward(60)

    tof2 = api.get_plane_distance()
    print(f"Height of 2'nd Step: {tof0-tof2}")

    time.sleep(1)

    api.single_fly_forward(70)

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

    print(f"Height of 1'st Step: {tof0-tof1}")
    print(f"Height of 2'nd Step: {tof0-tof2}")


    