import serial
import time
import struct
import copy


def main():
    # portName = '/dev/cu.usbmodem14201'
    portName = 'COM6'
    baudRate = 115200
    dataNumBytes = 8

    s = serialPlot(portName, baudRate, dataNumBytes, numSignals)
    s = serial.Serial(portName, baudRate)

    message = 1500;




    s.close()


if __name__ == '__main__':
    main()
