import pyhula
import time
import cv2
from datetime import datetime


api = pyhula.UserApi()

if not api.connect():
    print("Connection error")
else:
    print("Connection to station by WiFi")
    battery = api.get_battery()
    print("battery level: " + str(api.get_battery()))

    api.single_fly_takeoff()
    api.single_fly_touchdown()