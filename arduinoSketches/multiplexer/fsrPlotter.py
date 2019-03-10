# Adapted from: https://www.thepoorengineer.com/en/arduino-python-plot/
from threading import Thread
import serial
import time
import collections
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import struct
import copy


class serialPlot:
    def __init__(self, serialPort, serialBaud, plotLength, dataNumBytes, numSignals):
        self.port = serialPort
        self.baud = serialBaud
        self.plotMaxLength = plotLength
        self.dataNumBytes = dataNumBytes
        self.numSignals = numSignals
        self.rawData = bytearray(numSignals * dataNumBytes)
        self.dataType = None

        if dataNumBytes == 2:
            self.dataType = 'h'

        self.data = []
        for i in range(numSignals):
            self.data.append(collections.deque([0] * plotLength, maxlen=plotLength))

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

    def getSerialData(self, frame, lines, lineValueText, lineLabel, timeText):
        currentTimer = time.perf_counter()
        self.plotTimer = int((currentTimer - self.previousTimer) * 1000)
        self.previousTimer = currentTimer
        timeText.set_text('Plot Interval = ' + str(self.plotTimer) + ' ms')
        privateData = copy.deepcopy(self.rawData[:])
        for i in range(self.numSignals):
            data = privateData[(i*self.dataNumBytes):(self.dataNumBytes + i*self.dataNumBytes)]
            value,  = struct.unpack(self.dataType, data)
            self.data[i].append(value)
            lines[i].set_data(range(self.plotMaxLength), self.data[i])
            lineValueText[i].set_text('[' + lineLabel[i] + '] = ' + str(value))

    def backgroundThread(self):
        time.sleep(2)
        self.serialConnection.reset_input_buffer()

        while (self.isRun):
            if (struct.unpack('B', self.serialConnection.read())[0] is 0x9F) and (struct.unpack('B', self.serialConnection.read())[0] is 0x6E):
                self.rawData = self.serialConnection.read(self.numSignals * self.dataNumBytes)
                self.isReceiving = True

    def close(self):
        self.isRun = False
        self.thread.join()
        self.serialConnection.close()
        print('Disconnected...')



def main():
    portName = '/dev/cu.wchusbserial1410'
    baudRate = 115200
    maxPlotLength = 100
    dataNumBytes = 2
    numSignals = 8

    s = serialPlot(portName, baudRate, maxPlotLength, dataNumBytes, numSignals)
    s.readSerialStart()

    pltInterval = 20
    xmin = 0
    xmax = maxPlotLength
    ymin = 0
    ymax = 1024

    fig = plt.figure(figsize=(12, 6))
    ax = plt.axes(xlim=(xmin, xmax), ylim=(float(ymin - (ymax - ymin) / 10), float(ymax + (ymax - ymin) / 10)))
    ax.set_title("FSR Live Output",fontweight='bold',size=20)
    ax.set_xlabel("Time -->",fontweight='bold')
    ax.set_ylabel("Raw Analog Out",fontweight='bold')

    lineLabel = ['FSR1', 'FSR2', 'FSR3', 'FSR4', 'FSR5', 'FSR6', 'FSR7', 'FSR8']
    style = ['c-', 'm-', 'y-', '-k', '--c', '--m', '--y', '--k']
    timeText = ax.text(0.80, 0.95, '', transform=ax.transAxes)
    lines = []
    lineValueText = []
    for i in range(numSignals):
        lines.append(ax.plot([], [], style[i], label=lineLabel[i])[0])
        lineValueText.append(ax.text(0.05, 0.95-i*0.05, '', transform=ax.transAxes))

    anim = animation.FuncAnimation(fig, s.getSerialData, fargs=(lines, lineValueText, lineLabel, timeText), interval=pltInterval)    # fargs has to be a tuple

    plt.legend(loc='upper center', ncol=4)
    plt.xticks([])
    plt.show()

    s.close()


if __name__ == '__main__':
    main()
