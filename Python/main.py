from sklearn.decomposition import PCA
from threading import Thread
from sklearn import svm
from mpl_toolkits import mplot3d
import RPi.GPIO as GPIO
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import serial
import time
import struct
import copy
import math
import pickle


class Model:
    def __init__(self, model=None):
        # Class / object / constructor setup
        self.model = model
        self.trainingxdata = None
        self.trainingydata = None

    def get_training_data(self, s, data, n, classnum, trainnum):
        # Get user to do the gestures and record the data
        xdata = []
        ydata = []
        counter = 0
        for i in range(0, trainnum):
            print("Training iteration: {0}".format(i))
            for k in range(0, classnum):
                input("Class number: {0}".format(k))
                for j in range(0, n):
                    data.getData(s)
                    a = [int(x) for x in data.force]
                    xdata.append(a)
                    ydata.append(k)

        self.trainingxdata = np.array(xdata)
        self.trainingydata = np.array(ydata)

    def plot_pca(self, show=True):
        # Squash down the dimensions of FSR data and show in 3 dimensions for groupings
        self.pca = PCA(n_components=3)
        self.pca.fit(self.trainingxdata)
        Xpca = self.pca.fit_transform(self.trainingxdata)
        ax = plt.axes(projection='3d')

        for i in range(0, int(self.trainingydata.max()) + 1):
            Xtemp = Xpca[self.trainingydata == i]
            ax.scatter3D(Xtemp[:, 0], Xtemp[:, 1], Xtemp[:, 2], cmap='Greens')

        if show is True:
            plt.figure(1)
            plt.show()

    def trainSVM(self):
        # Create a SVM classifier using sklearn
        self.model = svm.SVC(kernel='rbf', gamma='scale')
        self.model.fit(self.trainingxdata, self.trainingydata)

    def predict(self, data):
        # Identify the gesture and return the result
        prediction = self.model.predict([data])
        return prediction

    def score(self, xdata, ydata):
        # How accurate was the model?
        score = self.model.score(xdata, ydata)
        return score

    def savemodel(self, filename):
        # Save with pickles so that retraining is not required
        pickle.dump(self, open(filename, 'wb'))

    def data_split(self, p):
        # Arrange the data into something that is useful
        data = np.hstack((self.trainingxdata, np.transpose(np.array([self.trainingydata]))))
        datashuff = np.array(data)
        np.random.shuffle(datashuff)

        cutoff = int(p * data.shape[0])
        self.trainingxdata = datashuff[0:cutoff, 0:-1]
        self.trainingydata = datashuff[0:cutoff, -1]

        self.testingxdata = datashuff[cutoff::, 0:-1]
        self.testingydata = datashuff[cutoff::, -1]


class DAQ:
    def __init__(self, serialPort, serialBaud, dataNumBytes, numSignals):
        # Class / object / constructor setup
        self.port = serialPort
        self.baud = serialBaud
        self.dataNumBytes = dataNumBytes
        self.numSignals = numSignals
        self.rawData = bytearray(numSignals * dataNumBytes)
        self.dataType = None
        self.isRun = True
        self.isReceiving = False
        self.thread = None
        self.dataOut = []

        if dataNumBytes == 2:
            self.dataType = 'h'

        # Connect to serial port
        print('Trying to connect to: ' + str(serialPort) + ' at ' + str(serialBaud) + ' BAUD.')
        try:
            self.serialConnection = serial.Serial(serialPort, serialBaud, timeout=4)
            print('Connected to ' + str(serialPort) + ' at ' + str(serialBaud) + ' BAUD.')
        except:
            print("Failed to connect with " + str(serialPort) + ' at ' + str(serialBaud) + ' BAUD.')

    def readSerialStart(self):
        # Create a thread
        if self.thread == None:
            self.thread = Thread(target=self.backgroundThread)
            self.thread.start()

            # Block till we start receiving values
            while self.isReceiving != True:
                time.sleep(0.1)

    def backgroundThread(self):
        # Pause and clear buffer to start with a good connection
        time.sleep(2)
        self.serialConnection.reset_input_buffer()

        # Read until closed
        while (self.isRun):
            self.getSerialData()
            self.isReceiving = True

    def getSerialData(self):
        # Initialize data out
        tempData = []

        # Check for header bytes and then read bytearray if header satisfied
        if (struct.unpack('B', self.serialConnection.read())[0] is 0x9F) and (struct.unpack('B', self.serialConnection.read())[0] is 0x6E):
            self.rawData = self.serialConnection.read(self.numSignals * self.dataNumBytes)

            # Copy raw data to new variable and set up the data out variable
            privateData = copy.deepcopy(self.rawData[:])

            # Loop through all the signals and decode the values to decimal
            for i in range(self.numSignals):
                data = privateData[(i*self.dataNumBytes):(self.dataNumBytes + i*self.dataNumBytes)]
                value, = struct.unpack(self.dataType, data)
                tempData.append(value)

        # Check if data is usable otherwise repeat (recursive function)
        if tempData:
            if (struct.unpack('B', self.serialConnection.read())[0] is 0xAE) and (struct.unpack('B', self.serialConnection.read())[0] is 0x72):
                self.dataOut = tempData
            else:
                return self.getSerialData()
        else:
            return self.getSerialData()

    def close(self):
        # Close the serial port connection
        self.isRun = False
        self.thread.join()
        self.serialConnection.close()

        print('Disconnected...')


class Sensors:
    def __init__(self, gyroScaleFactor, accScaleFactor, VCC, Resistor, tau):
        # Class / object / constructor setup
        self.gyroScaleFactor = gyroScaleFactor
        self.accScaleFactor = accScaleFactor
        self.VCC = VCC
        self.Resistor = Resistor
        self.tau = tau

        self.gx = None; self.gy = None; self.gz = None;
        self.ax = None; self.ay = None; self.az = None;

        self.gyroXcal = 0
        self.gyroYcal = 0
        self.gyroZcal = 0

        self.gyroRoll = 0
        self.gyroPitch = 0
        self.gyroYaw = 0

        self.roll = 0
        self.pitch = 0
        self.yaw = 0

        self.dtTimer = 0

        self.FSRvalues = []
        self.force = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

    def getRawSensorValues(self, s):
        # Get raw values from serial connection
        val = s.dataOut
        self.gx = val[0]
        self.gy = val[1]
        self.gz = val[2]
        self.ax = val[3]
        self.ay = val[4]
        self.az = val[5]
        self.FSRvalues = [val[6], val[7], val[8], val[9], val[10], val[11], val[12], val[13], val[14], val[15], val[16]]

    def calibrateGyro(self, s, N):
        # Display message
        print("Calibrating gyro with " + str(N) + " points. Do not move!")

        # Take N readings for each coordinate and add to itself
        for ii in range(N):
            self.getRawSensorValues(s)
            self.gyroXcal += self.gx
            self.gyroYcal += self.gy
            self.gyroZcal += self.gz

        # Find average offset value
        self.gyroXcal /= N
        self.gyroYcal /= N
        self.gyroZcal /= N

        # Display message and restart timer for comp filter
        print("Calibration complete")
        self.dtTimer = time.time()

    def processIMUvalues(self):
        # Subtract the offset calibration values
        self.gx -= self.gyroXcal
        self.gy -= self.gyroYcal
        self.gz -= self.gyroZcal

        # Convert to instantaneous degrees per second
        self.gx /= self.gyroScaleFactor
        self.gy /= self.gyroScaleFactor
        self.gz /= self.gyroScaleFactor

        # Convert to g force
        self.ax /= self.accScaleFactor
        self.ay /= self.accScaleFactor
        self.az /= self.accScaleFactor

    def compFilter(self):
        # Get the processed values from IMU
        self.processIMUvalues()

        # Get delta time and record time for next call
        dt = time.time() - self.dtTimer
        self.dtTimer = time.time()

        # Acceleration vector angle
        accPitch = math.degrees(math.atan2(self.ay, self.az))
        accRoll = math.degrees(math.atan2(self.ax, self.az))

        # Gyro integration angle
        self.gyroRoll -= self.gy * dt
        self.gyroPitch += self.gx * dt
        self.gyroYaw += self.gz * dt
        self.yaw = self.gyroYaw

        # Comp filter
        self.roll = (self.tau)*(self.roll - self.gy*dt) + (1-self.tau)*(accRoll)
        self.pitch = (self.tau)*(self.pitch + self.gx*dt) + (1-self.tau)*(accPitch)

    def processFSRvalues(self):
        # Loop through all values
        for ii in range(len(self.FSRvalues)):
            # Analog value to voltage
            fsrV = self.FSRvalues[ii] * self.VCC / 1023.0

            # Use voltage and static resistor value to calculate FSR resistance
            try:
                fsrR = ((self.VCC - fsrV) * self.Resistor) / fsrV
            except:
                fsrR = 1e6

            # Guesstimate force based on slopes in figure 3 of FSR datasheet (conductance)
            fsrG = 1.0 / fsrR

            # Break parabolic curve down into two linear slopes
            if (fsrR <= 600):
                self.force[ii] = (fsrG - 0.00075) / 0.00000032639
            else:
                self.force[ii] =  fsrG / 0.000000642857

        # Write the last entry of force to be the average value
        self.force[11] = np.mean(self.force)

    def getData(self,s):
        # Get data from serial
        self.getRawSensorValues(s)

        # Process IMU values
        self.compFilter()

        # Process FSR values
        self.processFSRvalues()

    def logData(self, s, T):
        # Set up timer, counter, and temp data storage
        startTime = time.perf_counter()
        count = 0
        tempData = []

        # Run for T seconds
        while time.perf_counter() < startTime + T:
            self.getData(s)
            tempData.append([time.perf_counter() - startTime] + self.force + [self.roll, self.pitch, self.yaw])
            count += 1

        # Close serial connection, write data, and display sampling rate
        print("Samping rate: ", count / (time.perf_counter() - startTime), " Hz")

        # Write data to CSV
        df = pd.DataFrame(tempData, columns=['Time', 'FSR1', 'FSR2', 'FSR3', 'FSR4', 'FSR5', 'FSR6',
                                   'FSR7', 'FSR8', 'FSR9', 'FSR10', 'FSR11', 'Avg', 'Roll', 'Pitch', 'Yaw'])

        df.to_csv('data.csv', index=None, header=True)


class robotArm:
    def __init__(self):
        # Joint PWM ranges
        self.joint1Range = [500,2300]
        self.joint2Range = [1000,2000]
        self.joint3Range = [500,1200]
        self.joint4Range = [1100,1100]

    def startControl(self):
        # Run `pinout` to see the numbers
        GPIO.setmode(GPIO.BOARD)

        # Set up PWM pins on GPIO
        GPIO.setup(12, GPIO.OUT)
        GPIO.setup(13, GPIO.OUT)
        GPIO.setup(18, GPIO.OUT)
        GPIO.setup(19, GPIO.OUT)

        # Initialize all servos to center position
        self.joint1 = GPIO.PWM(12, 50)
        self.joint2 = GPIO.PWM(13, 50)
        self.joint3 = GPIO.PWM(18, 50)
        self.joint4 = GPIO.PWM(19, 50)

        # Write start position
        self.joint1.start(7.5)
        self.joint2.start(7.5)
        self.joint3.start(7.5)
        self.joint4.start(7.5)

    def updateState(self, state):
        # percentage / (20 ms * unit conversion)
        dutyCycleScale = 100 / (20*1000)

        # Check the different states and write a pule
        if state == 1:
            # Fist
            self.joint4.ChangeDutyCycle(self.joint4Range[1]*dutyCycleScale)
        elif state == 2:
            # Rest
            self.joint4.ChangeDutyCycle(self.joint4Range[0]*dutyCycleScale)
        elif state == 3:
            # Extension
            self.joint1.ChangeDutyCycle(self.joint1Range[0]*dutyCycleScale)
        elif state == 4:
            # Flexion
            self.joint1.ChangeDutyCycle(self.joint1Range[1]*dutyCycleScale)
        elif state == 5:
            # Forward
            self.joint2.ChangeDutyCycle(self.joint2Range[0]*dutyCycleScale)
            self.joint3.ChangeDutyCycle(self.joint3Range[1]*dutyCycleScale)
        elif state == 6:
            # Back
            self.joint2.ChangeDutyCycle(self.joint2Range[1]*dutyCycleScale)
            self.joint3.ChangeDutyCycle(self.joint3Range[0]*dutyCycleScale)
        else:
            print("No state found")

    def endControl(self):
        # Stop writing PWM signal to servos
        self.joint1.stop()
        self.joint2.stop()
        self.joint3.stop()
        self.joint4.stop()

        # Clean up ports used
        GPIO.cleanup()


def main():
    # Set up serial connection
    portName = '/dev/rfcomm0'
    baudRate = 115200
    dataNumBytes = 2
    numSignals = 17

    s = DAQ(portName, baudRate, dataNumBytes, numSignals)
    s.readSerialStart()

    # Set up sensors
    numCalibrationPoints = 3000
    gyroScaleFactor = 131.0
    accScaleFactor = 16384.0
    VCC = 4.98
    Resistor = 5100.0
    tau = 0.98

    data = Sensors(gyroScaleFactor, accScaleFactor, VCC, Resistor, tau)
    data.calibrateGyro(s, numCalibrationPoints)

    # Set up robot arm
    bot = robotArm()
    bot.startControl()

    # set up, train, and save model
    model = Model()
    model.get_training_data(s, data, 2500, 8, 3)
    model.plot_pca()
    model.trainSVM()
    model.savemodel('8x3x2500-Pi')

    # Realtime control
    T = int(input("Enter how many seconds to run real time control: "))
    startTime = time.time()

    while(time.time() < (startTime + T)):
        data.getData(s)
        pred = model.predict(data.force)
        bot.updateclass(pred[0])
        print(pred)

    # Close all the connections and end program
    s.close()
    bot.endControl()
    print("Closed all")


if __name__ == '__main__':
    main()
