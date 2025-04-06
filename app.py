import pyhula
import time
import threading

api = pyhula.UserApi()

if not api.connect():
    print("Connection error")
else:
    print("Connection to station by WiFi")
    battery = api.get_battery()
    print("battery level: " + str(api.get_battery()))
    t1 = threading.Thread(target=api.single_fly_radius_around, args=30)
    t2 = threading.Thread(target=api.single_fly_down, args=20)
    t1.start()
    t2.start()
    t1.join()
    t2.join()
    api.single_fly_touchdown()
