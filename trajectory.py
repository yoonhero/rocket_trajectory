from scipy.integrate import cumtrapz
import numpy as np
import time
import math as m
import matplotlib.pyplot as plt
import json
import sys
import matplotlib.animation as animation
tol = sys.float_info.epsilon * 10

from serial_utils import get_imu_data

def Rx(theta):
    return np.matrix([[1, 0, 0], [0, m.cos(theta), -m.sin(theta)], [0, m.sin(theta), m.cos(theta)]])

def Ry(theta):
    return np.matrix([[m.cos(theta), 0, m.sin(theta)], [0, 1, 0], [-m.sin(theta), 0, m.cos(theta)]])

def Rz(theta):
    return np.matrix([[m.cos(theta), -m.sin(theta), 0], [m.sin(theta), m.cos(theta), 0], [0, 0, 1]])

def get_acc(current_val, thetas):
    target_val = np.array([0, 0, 9.82])

    R = Rx(thetas[0]) * Ry(thetas[1]) * Rz(thetas[2])
    R_inv = np.linalg.inv(R)

    result = R_inv @ current_val.T - target_val
    return result

### UMMM vanila calibration z
def calibrate(data):
    data["ax"] += 1.02
    data["ay"] += 0.09
    data["gy"] += 0.02
    data["gz"] += 0.04
    return data

class Theta():
    def __init__(self):
        self.acc = []
        self.dts = []
        self.thetas = []

    def vanila_filter(self, data, dt):
        self.acc.append(data)
        self.dts.append(dt)

        # gx, gy, gz = data
        current_theta = [d*dt for d in data]
        if len(self.thetas) > 0:
            current_theta += self.thetas[-1] 
        self.thetas.append(current_theta)

        return current_theta
    
    def save_data(self):
        with open("data.json", "w", encoding="utf-8") as f:
            to_dump = {"acc": self.acc, "dts": self.dts, "thetas": self.thetas}
            json.dump(to_dump, f)


datas = []
imu_datas = get_imu_data("/dev/cu.usbserial-14230", baudrate=115200)
start = time.time()

theta_filter = Theta()
z = [0]

fig = plt.figure()
ax = fig.add_subplot()
fig.show()

def animate(i):
    global start
    # try:
        # for data in imu_datas:
    data = next(imu_datas)
    dt = time.time() - start

    gyro = ["gx", "gy", "gz"]
    acc = ["ax", "ay", "az"]
    a_data = [data[key] for key in data.keys() if key in acc]
    a_matrix = np.array(a_data)

    g_data = [data[key] for key in data.keys() if key in gyro]
    thetas = theta_filter.vanila_filter(g_data, dt)
    acc = get_acc(a_matrix, thetas)
    z_acc = acc[0, -1]
    print(z_acc)
    d_z = 1/2*z_acc*(dt**2)

    z.append(z[-1]+d_z)        

    ax.clear()
    ax.plot(list(range(len(z))), z, color="r")
    # ax.set_xlim(left=max(0, i-n))

    start = time.time()
    # except: 
    #     theta_filter.save_data()

ani = animation.FuncAnimation(fig, animate, interval=50)
plt.show()






    