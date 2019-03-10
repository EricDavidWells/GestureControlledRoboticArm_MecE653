from statistics import mean
import matplotlib.pyplot as plt
import numpy as np
import serial
import time
import struct
import copy
import math


class DAQ:
    def __init__(self, serialPort, serialBaud, dataNumBytes, numSignals):
        self.port = serialPort
        self.baud = serialBaud
        self.dataNumBytes = dataNumBytes
        self.numSignals = numSignals
        self.rawData = bytearray(numSignals * dataNumBytes)
        self.dataType = None

        if dataNumBytes == 2:
            self.dataType = 'h'

        self.data = []
        for i in range(numSignals):
            self.data.append([0])

        print('Trying to connect to: ' + str(serialPort) + ' at ' + str(serialBaud) + ' BAUD.')
        try:
            self.serialConnection = serial.Serial(serialPort, serialBaud, timeout=4)
            print('Connected to ' + str(serialPort) + ' at ' + str(serialBaud) + ' BAUD.')
        except:
            print("Failed to connect with " + str(serialPort) + ' at ' + str(serialBaud) + ' BAUD.')

    def readSerialStart(self):
        time.sleep(1)
        self.serialConnection.reset_input_buffer()

    def getSerialData(self):
        if (struct.unpack('B', self.serialConnection.read())[0] is 0x9F) and (struct.unpack('B', self.serialConnection.read())[0] is 0x6E):
            self.rawData = self.serialConnection.read(self.numSignals * self.dataNumBytes)

            privateData = copy.deepcopy(self.rawData[:])
            temp = []

            for i in range(self.numSignals):
                data = privateData[(i*self.dataNumBytes):(self.dataNumBytes + i*self.dataNumBytes)]
                value,  = struct.unpack(self.dataType, data)
                self.data[i].append(value)
                temp.append(value)

        if temp:
            return temp ########### Change this variable name. Do we need to have self.rawData???
        else:
            getSerialData(self)

    def close(self):
        self.serialConnection.close()
        print('Disconnected...')


def calibrateGyro(s, N):

    # Display message
    print("Calibrating gyro with " + str(N) + "points. Do not move!")

    # Initialize
    gyro_x_cal = 0
    gyro_y_cal = 0
    gyro_z_cal = 0

    # Take N readings for each coordinate adding to itself
    for ii in range(N):
        data = s.getSerialData()
        gyro_x_cal += data[0];
        gyro_y_cal += data[1];
        gyro_z_cal += data[2];

    # Find average value
    gyro_x_cal /= N;
    gyro_y_cal /= N;
    gyro_z_cal /= N;

    print("Calibration complete")

    return gyro_x_cal, gyro_y_cal, gyro_z_cal


def sensorRead(s, gyro_x_cal, gyro_y_cal, gyro_z_cal, scaleFactorGyro, scaleFactorAcc):

    # Get data
    data = s.getSerialData()

    # Subtract the offset calibration value
    data[0] -= gyro_x_cal
    data[1] -= gyro_y_cal
    data[2] -= gyro_z_cal

    # Convert to instantaneous degrees per second
    w_x = float(data[0]) / float(scaleFactorGyro);
    w_y = float(data[1]) / float(scaleFactorGyro);
    w_z = float(data[2]) / float(scaleFactorGyro);

    # Convert to g force
    a_x = float(data[3]) / float(scaleFactorAcc);
    a_y = float(data[4]) / float(scaleFactorAcc);
    a_z = float(data[5]) / float(scaleFactorAcc);

    return w_x, w_y, w_z, a_x, a_y, a_z


def compFilter(w_x, w_y, w_z, a_x, a_y, a_z, roll, pitch, dtTimer, tau):

    # Get delta time
    dt = time.time() - dtTimer
    dtTimer = time.time()

    # Acceleration vector angle
    accPitch = math.degrees(atan2(a_y, a_z))
    accRoll = math.degrees(atan2(a_x, a_z))

    # Gyro integration angle
    gyroPitch += w_x * dt
    gyroRoll -= w_y * dt
    gyroYaw += w_z * dt

    # Comp filter
    roll = (tau)*(roll - w_y*dt) + (1-tau)*(accRoll);
    pitch = (tau)*(pitch + w_x*dt) + (1-tau)*(accPitch);

    return roll, pitch, dtTimer


def main():
    portName = '/dev/cu.wchusbserial1420'
    baudRate = 115200
    dataNumBytes = 2
    numSignals = 4

    numCalibrationPoints = 1000

    scaleFactorGyro = 65.5 # 250 deg/s --> 131, 500 deg/s --> 65.5, 1000 deg/s --> 32.8, 2000 deg/s --> 16.4
    scaleFactorAcc = 8192 # 2g --> 16384 , 4g --> 8192 , 8g --> 4096, 16g --> 2048
    dtTimer = 0
    roll = 0
    pitch = 0

    tau = 0.98

    s = DAQ(portName, baudRate, dataNumBytes, numSignals)
    s.readSerialStart()

    gyro_x_cal, gyro_y_cal, gyro_z_cal = calibrateGyro(s,numCalibrationPoints)



    w_x, w_y, w_z, a_x, a_y, a_z = sensorRead(s, gyro_x_cal, gyro_y_cal, gyro_z_cal, scaleFactorGyro, scaleFactorAcc)
    roll, pitch, dtTimer = compFilter(w_x, w_y, w_z, a_x, a_y, a_z, roll, pitch, dtTimer, tau)


    #
    # dataPoints = 2000 # Change to time... Same with x axis
    #
    # for ii in range(dataPoints):
    #     rawData = s.getSerialData()
    #
    #
    #     print(data, ii)
    #
    #     pitch.append(data[0])
    #     gyroPitch.append(data[1])
    #     accPitch.append(data[2])
    #     freq.append(data[3])
    #
    # print('Average frequency was: ' + str(round(mean(freq),2)) + ' Hz')
    #
    # x = np.arange(len(pitch))
    #
    # plt.plot(x,pitch,'-k',linewidth=3,label='Complementary Filter')
    # plt.plot(x,gyroPitch,'-g',linewidth=1,label='Gyroscope Angle')
    # plt.plot(x,accPitch,'-b',linewidth=1,label='Accelerometer Angle')
    #
    # plt.xlabel('Iteration Index')
    # plt.ylabel('Angle (deg)')
    # plt.legend(loc='upper left')

    s.close()
    # plt.show()


if __name__ == '__main__':
    main()
