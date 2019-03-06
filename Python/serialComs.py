# Adapted from https://www.thepoorengineer.com/en/arduino-python-plot/
from threading import Thread
import serial
import time
import collections
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
            self.dataType = 'h'     # 2 byte integer
        elif dataNumBytes == 4:
            self.dataType = 'f'     # 4 byte float

        self.data = []

        for i in range(numSignals):
            self.data.append([0])

        self.isRun = True
        self.isReceiving = False
        self.thread = None
        self.plotTimer = 0
        self.previousTimer = 0

        print('Trying to connect to: ' + str(serialPort) + ' at ' + str(serialBaud) + ' BAUD.')
        try:
            self.serialConnection = serial.Serial(serialPort, serialBaud, timeout=4)
            print('Connected to ' + str(serialPort) + ' at ' + str(serialBaud) + ' BAUD.')
        except:
            print("Failed to connect with " + str(serialPort) + ' at ' + str(serialBaud) + ' BAUD.')

    def readSerialStart(self):
        if self.thread == None:
            self.thread = Thread(target=self.backgroundThread)

            self.thread.start()
            # Block till we start receiving values
            while self.isReceiving != True:
                time.sleep(0.1)

    def getSerialData(self):
        privateData = copy.deepcopy(self.rawData[:])
        temp = []

        for i in range(self.numSignals):
            data = privateData[(i*self.dataNumBytes):(self.dataNumBytes + i*self.dataNumBytes)]
            value,  = struct.unpack(self.dataType, data)
            self.data[i].append(value)    # we get the latest data point and append it to our array
            temp.append(value)

        print(temp)

    def backgroundThread(self):    # retrieve data
        time.sleep(1.0)  # give some buffer time for retrieving data
        self.serialConnection.reset_input_buffer()
        self.serialConnection.timeout = 0

        # print(self.serialConnection._timeout)
        self.serialConnection.read(16*20)
        # print(self.rawData)
        self.serialConnection.timeout = None
        # print(self.serialConnection._timeout)

        while (self.isRun):
            self.serialConnection.readinto(self.rawData)
            self.isReceiving = True
            # print(self.rawData)

    def close(self):
        self.isRun = False
        self.thread.join()
        self.serialConnection.close()
        print('Disconnected...')
        # df = pd.DataFrame(self.csvData)
        # df.to_csv('../Desktop/data.csv')


def main():
    portName = '/dev/cu.wchusbserial1420' #'/dev/cu.usbmodem14201'
    baudRate = 115200
    dataNumBytes = 2        # number of bytes of 1 data point - 2 bytes for INT
    numSignals = 8

    s = serialPlot(portName, baudRate, dataNumBytes, numSignals)
    s.readSerialStart()

    for ii in range(10000):
        s.getSerialData()

    s.close()


if __name__ == '__main__':
    main()
