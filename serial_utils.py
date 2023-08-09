import serial
import io

def get_imu_data(port, baudrate):
    with serial.Serial(port, baudrate, timeout=1) as ser:
        if not ser.is_open:
            raise TimeoutError

        while True:
            line = ser.readline()

            data = line.decode().strip().split(",")
            appropriate = len(data) == 7

            if not appropriate: continue

            data = [float(d) for d in data]
            # ax, ay, az, gx, gy, gz, temp = data
            columns = ["ax", "ay", "az", "gx", "gy", "gz", "temp"]
            row = {k: v for k, v in zip(columns, data)}

            yield row
