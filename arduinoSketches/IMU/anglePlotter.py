from statistics import mean
import matplotlib.pyplot as plt
import numpy as np
import serial
import time
import struct
import copy


class serialPlot:
    def __init__(self, serialPort, serialBaud, dataNumBytes, numSignals):
        self.port = serialPort
        self.baud = serialBaud
        self.dataNumBytes = dataNumBytes
        self.numSignals = numSignals
        self.rawData = bytearray(numSignals * dataNumBytes)
        self.dataType = None

        if dataNumBytes == 2:
            self.dataType = 'h'
        elif dataNumBytes == 4:
            self.dataType = 'f'

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
        print("Do not move! Gyro calibrating...")
        for ii in range(6):
            print('.', end='', flush=True)
            time.sleep(2)
        print()
        self.serialConnection.reset_input_buffer()

    def getSerialData(self):
        if (int(self.serialConnection.read().hex(),16) is 159) and (int(self.serialConnection.read().hex(),16) is 110):
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


def main():
    portName = '/dev/cu.wchusbserial1420'
    baudRate = 115200
    dataNumBytes = 2
    numSignals = 4
    dataPoints = 2000

    s = serialPlot(portName, baudRate, dataNumBytes, numSignals)
    s.readSerialStart()

    pitch = []
    gyroPitch = []
    accelPitch = []
    freq = []

    for ii in range(dataPoints):
        data = s.getSerialData()
        print(data, ii)

        pitch.append(data[0])
        gyroPitch.append(data[1])
        accelPitch.append(data[2])
        freq.append(data[3])

    print('Average frequency was: ' + str(round(mean(freq),2)) + ' Hz')

    x = np.arange(len(pitch))

    plt.plot(x,pitch,'-r',linewidth=5,label='Complementary Filter')
    plt.plot(x,gyroPitch,'-g',linewidth=2,label='Gyroscope Angle')
    plt.plot(x,accelPitch,'-b',linewidth=2,label='Accelerometer Angle')

    plt.xlabel('Iteration Index')
    plt.ylabel('Angle (deg)')
    plt.legend(loc='upper left')

    s.close()
    plt.show()


if __name__ == '__main__':
    main()
