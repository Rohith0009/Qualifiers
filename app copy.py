import pyhula
import time
import threading
import math

api = pyhula.UserApi()


def circle_up(radius, height_increase, num_steps):
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

        api.single_fly_curvilinearFlight(dx, dy, z)
        time.sleep(0.1)


if not api.connect():
    print("Connection error")
else:
    print("Connection to station by WiFi")
    battery = api.get_battery()
    print("battery level: " + str(api.get_battery()))
    api.single_fly_takeoff()

    circle_up(50, 20, 100)

    api.single_fly_touchdown()
