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
        time.sleep(1.0)
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
    portName = '/dev/cu.usbmodem14201'
    baudRate = 115200
    dataNumBytes = 2
    numSignals = 8
    dataPoints = 1000

    s = serialPlot(portName, baudRate, dataNumBytes, numSignals)
    s.readSerialStart()

    timer = time.time()

    for ii in range(dataPoints):
        data = s.getSerialData()
        print(data, ii)

    print('Average sample rate: ' + str(int(dataPoints/(time.time()-timer))) + ' Hz')
    s.close()


if __name__ == '__main__':
    main()
