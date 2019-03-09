from statistics import mean
import matplotlib.pyplot as plt
import numpy as np
import serial
import time
import struct
import copy


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
        time.sleep(1.0)
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

            return temp

    def close(self):
        self.serialConnection.close()
        print('Disconnected...')



def calibrateGyro(N):
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

    # Return array of offsets
    calibration = [gyro_x_cal, gyro_y_cal, gyro_z_cal]
    print("Calibration complete")

    return calibration


# def compFilter(gyro_x, gyro_y, gyro_z, acc_x, acc_y, acc_z):
#     # 250 deg/s --> 131, 500 deg/s --> 65.5, 1000 deg/s --> 32.8, 2000 deg/s --> 16.4
#     long scaleFactorGyro = 65.5;
#
#     # 2g --> 16384 , 4g --> 8192 , 8g --> 4096, 16g --> 2048
#     long scaleFactorAccel = 8192;
#
#     tau = 0.98
#
#     freq = 1/((micros() - dtTimer) * 1e-6);
#     dtTimer = micros();
#     dt = 1/freq;
#
#     // Subtract the offset calibration value
#     gyro_x -= gyro_x_cal;
#     gyro_y -= gyro_y_cal;
#     gyro_z -= gyro_z_cal;
#
#     // Convert to instantaneous degrees per second
#     rotation_x = (double)gyro_x / (double)scaleFactorGyro;
#     rotation_y = (double)gyro_y / (double)scaleFactorGyro;
#     rotation_z = (double)gyro_z / (double)scaleFactorGyro;
#
#     // Convert to g force
#     accel_x = (double)acc_x / (double)scaleFactorAccel;
#     accel_y = (double)acc_y / (double)scaleFactorAccel;
#     accel_z = (double)acc_z / (double)scaleFactorAccel;
#
#     // Complementary filter
#     accelPitch = atan2(accel_y, accel_z) * RAD_TO_DEG;
#     accelRoll = atan2(accel_x, accel_z) * RAD_TO_DEG;
#
#     pitch = (tau)*(pitch + rotation_x*dt) + (1-tau)*(accelPitch);
#     roll = (tau)*(roll - rotation_y*dt) + (1-tau)*(accelRoll);
#
#     gyroPitch += rotation_x*dt;
#     gyroRoll -= rotation_y*dt;
#     gyroYaw += rotation_z*dt;
#

def main():
    portName = '/dev/cu.wchusbserial1420'
    baudRate = 115200
    dataNumBytes = 2
    numSignals = 4

    calibrationPoints = 1000;

    s = DAQ(portName, baudRate, dataNumBytes, numSignals)
    s.readSerialStart()

    cal = calibrateGyro(calibrationPoints):

    # dataPoints = 2000 # Change to time... Same with x axis
    #
    # for ii in range(dataPoints):
    #     data = s.getSerialData()
    #     print(data, ii)
    #
    #     pitch.append(data[0])
    #     gyroPitch.append(data[1])
    #     accelPitch.append(data[2])
    #     freq.append(data[3])
    #
    # print('Average frequency was: ' + str(round(mean(freq),2)) + ' Hz')
    #
    # x = np.arange(len(pitch))
    #
    # plt.plot(x,pitch,'-k',linewidth=3,label='Complementary Filter')
    # plt.plot(x,gyroPitch,'-g',linewidth=1,label='Gyroscope Angle')
    # plt.plot(x,accelPitch,'-b',linewidth=1,label='Accelerometer Angle')
    #
    # plt.xlabel('Iteration Index')
    # plt.ylabel('Angle (deg)')
    # plt.legend(loc='upper left')

    s.close()
    # plt.show()


if __name__ == '__main__':
    main()
