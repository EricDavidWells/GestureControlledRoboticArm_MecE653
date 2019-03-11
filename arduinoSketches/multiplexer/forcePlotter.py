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
        # Class / object / constructor setup
        self.port = serialPort
        self.baud = serialBaud
        self.plotMaxLength = plotLength
        self.dataNumBytes = dataNumBytes
        self.numSignals = numSignals
        self.rawData = bytearray(numSignals * dataNumBytes)
        self.dataType = None
        self.VCC = 4.98
        self.Resistor = 5100.0

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

        # Connect to serial port
        print('Trying to connect to: ' + str(serialPort) + ' at ' + str(serialBaud) + ' BAUD.')
        try:
            self.serialConnection = serial.Serial(serialPort, serialBaud, timeout=4)
            print('Connected to ' + str(serialPort) + ' at ' + str(serialBaud) + ' BAUD.')
        except:
            print("Failed to connect with " + str(serialPort) + ' at ' + str(serialBaud) + ' BAUD.')

    def readSerialStart(self):
        # Set up thread for plotting and thread for DAQ
        if self.thread == None:
            self.thread = Thread(target=self.backgroundThread)
            self.thread.start()

            # Block till we start receiving values
            while self.isReceiving != True:
                time.sleep(0.1)

    def getSerialData(self, frame, lines, lineValueText, lineLabel, timeText):
        # Calculate plot refresh rate
        currentTimer = time.perf_counter()
        self.plotTimer = int((currentTimer - self.previousTimer) * 1000)
        self.previousTimer = currentTimer
        timeText.set_text('Plot Interval = ' + str(self.plotTimer) + ' ms')

        # Copy raw data to new private variable and loop through signals
        privateData = copy.deepcopy(self.rawData[:])
        for i in range(self.numSignals):
            data = privateData[(i*self.dataNumBytes):(self.dataNumBytes + i*self.dataNumBytes)]
            value,  = struct.unpack(self.dataType, data)

            # Analog value to voltage
            fsrV = value * self.VCC / 1023.0

            # Use voltage and static resistor value to calculate FSR resistance
            try:
                fsrR = ((self.VCC - fsrV) * self.Resistor) / fsrV
            except:
                fsrR = 1e6

            # Guesstimate force based on slopes in figure 3 of FSR datasheet (conductance)
            fsrG = 1.0 / fsrR

            # Break parabolic curve down into two linear slopes
            if (fsrR <= 600):
                value = (fsrG - 0.00075) / 0.00000032639
            else:
                value =  fsrG / 0.000000642857

            # Add value to data array and update plot values
            self.data[i].append(value)
            lines[i].set_data(range(self.plotMaxLength), self.data[i])
            lineValueText[i].set_text('[' + lineLabel[i] + '] = ' + str(round(value)))

    def backgroundThread(self):
        # Pause and clear buffer to start with a good connection
        time.sleep(2)
        self.serialConnection.reset_input_buffer()

        while (self.isRun):
            # Check for header bytes and then read bytearray if header satisfied
            if (struct.unpack('B', self.serialConnection.read())[0] is 0x9F) and (struct.unpack('B', self.serialConnection.read())[0] is 0x6E):
                self.rawData = self.serialConnection.read(self.numSignals * self.dataNumBytes)
                self.isReceiving = True

    def close(self):
        # Close the serial port connection and join threads
        self.isRun = False
        self.thread.join()
        self.serialConnection.close()
        print('Disconnected...')



def main():
    # Set up serial connection
    portName = 'COM10' #/dev/cu.wchusbserial1410
    baudRate = 115200
    maxPlotLength = 100
    dataNumBytes = 2
    numSignals = 8

    s = serialPlot(portName, baudRate, maxPlotLength, dataNumBytes, numSignals)
    s.readSerialStart()

    # Set plot values
    pltInterval = 20
    xmin = 0
    xmax = maxPlotLength
    ymin = 0
    ymax = 1024

    # Create plot elements
    fig = plt.figure(figsize=(12, 6))
    ax = plt.axes(xlim=(xmin, xmax), ylim=(float(ymin - (ymax - ymin) / 10), float(ymax + (ymax - ymin) / 10)))
    ax.set_title("FSR Live Output",fontweight='bold',size=20)
    ax.set_xlabel("Time -->",fontweight='bold')
    ax.set_ylabel("Force [g]",fontweight='bold')
    lineLabel = ['FSR1', 'FSR2', 'FSR3', 'FSR4', 'FSR5', 'FSR6', 'FSR7', 'FSR8']
    style = ['c-', 'm-', 'y-', '-k', '--c', '--m', '--y', '--k']
    timeText = ax.text(0.80, 0.95, '', transform=ax.transAxes)

    # Plot values and update the animation
    lines = []
    lineValueText = []
    for i in range(numSignals):
        lines.append(ax.plot([], [], style[i], label=lineLabel[i])[0])
        lineValueText.append(ax.text(0.05, 0.95-i*0.05, '', transform=ax.transAxes))

    anim = animation.FuncAnimation(fig, s.getSerialData, fargs=(lines, lineValueText, lineLabel, timeText), interval=pltInterval)    # fargs has to be a tuple

    # Show the plot, add legend, and remove x axis
    plt.legend(loc='upper center', ncol=4)
    plt.xticks([])
    plt.show()

    # Closer serial connection
    s.close()



if __name__ == '__main__':
    main()
