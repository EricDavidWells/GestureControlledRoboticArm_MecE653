import serial
import struct
import time
from threading import Thread
import queue
import math
import numpy as np
import pandas as pd
from sklearn.decomposition import PCA
from sklearn import svm
import pickle
import matplotlib.pyplot as plt
from mpl_toolkits import mplot3d


class Model:
    def __init__(self, model=None):
        self.model = model
        self.trainingxdata = None
        self.trainingydata = None

    def get_training_data(self, q, data, n, classnum, trainnum):
        xdata = []
        ydata = []
        counter = 0
        for i in range(0, trainnum):
            print("Training iteration: {0}".format(i))
            for k in range(0, classnum):
                print("Class number: {0} starting in 1 second..".format(k))
                time.sleep(1)
                q.empty()
                for j in range(0, n):
                    data.getData(q)
                    a = [int(x) for x in data.force]
                    # b = [int(data.ax),int(data.ay),int(data.az),int(data.gx),int(data.gy),int(data.gz),int(data.dtTimer)]
                    # c = a+b
                    xdata.append(a)
                    ydata.append(k)

        self.trainingxdata = np.array(xdata)
        self.trainingydata = np.array(ydata)

    def plot_pca(self, show=True):
        self.pca = PCA(n_components=3)
        self.pca.fit(self.trainingxdata)
        Xpca = self.pca.fit_transform(self.trainingxdata)

        ax = plt.axes(projection='3d')
        for i in range(0, int(self.trainingydata.max()) + 1):
            Xtemp = Xpca[self.trainingydata == i]
            ax.scatter3D(Xtemp[:, 0], Xtemp[:, 1], Xtemp[:, 2], cmap='Greens')
            # ax.scatter3D(Xtemp[0::100][:, 0], Xtemp[0::100][:, 1], Xtemp[0::100][:, 2], cmap='Greens')
            ax.set_xlabel("PCA Axis 1")
            ax.set_ylabel("PCA Axis 2")
            ax.set_zlabel("PCA Axis 3")

        if show is True:
            plt.figure(1)
            plt.show()

    def trainSVM(self):
        self.model = svm.SVC(kernel='rbf', gamma='scale')
        self.model.fit(self.trainingxdata, self.trainingydata)

    def predict(self, data):
        prediction = self.model.predict([data])
        return prediction

    def score(self, xdata, ydata):
        score = self.model.score(xdata, ydata)
        return score

    def savemodel(self, filename):
        pickle.dump(self, open(filename, 'wb'))

    def data_split(self, p):
        """
        splits data into training and testing data by percentage p.
        :param data: ndarray of total data to be split
        :param p: percentage of data to be used for training
        :return: data split into training and testing
        """

        data = np.hstack((self.trainingxdata, np.transpose(np.array([self.trainingydata]))))
        datashuff = np.array(data)
        np.random.shuffle(datashuff)

        cutoff = int(p * data.shape[0])
        self.trainingxdata = datashuff[0:cutoff, 0:-1]
        self.trainingydata = datashuff[0:cutoff, -1]

        self.testingxdata = datashuff[cutoff::, 0:-1]
        self.testingydata = datashuff[cutoff::, -1]


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

    def getRawSensorValues(self, q):
        # Get raw values from serial connection
        val = q.get()

        self.gx = val[0]
        self.gy = val[1]
        self.gz = val[2]
        self.ax = val[3]
        self.ay = val[4]
        self.az = val[5]
        self.FSRvalues = [val[6], val[7], val[8], val[9], val[10], val[11], val[12], val[13], val[14], val[15], val[16]]

        q.task_done()

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

    def getData(self, s):
        # Get current time
        timer = time.perf_counter()

        # Stabilize sampling rate to 200 Hz
        while (time.perf_counter() < timer + 0.005):
            pass

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
        print("Sampling rate: ", count / (time.perf_counter() - startTime), " Hz")

        # Write data to CSV
        df = pd.DataFrame(tempData, columns=['Time', 'FSR1', 'FSR2', 'FSR3', 'FSR4', 'FSR5', 'FSR6',
                                   'FSR7', 'FSR8', 'FSR9', 'FSR10', 'FSR11', 'Avg', 'Roll', 'Pitch', 'Yaw'])

        df.to_csv('data.csv', index=None, header=True)


def get_serial_data(s):
    while True:
        try:
            if (struct.unpack('B', s.read())[0] is 0x9F) and (
                    struct.unpack('B', s.read())[0] is 0x6E):
                data = s.read(34)
                # print(data)

                if (struct.unpack('B', s.read())[0] is 0xAE) and (
                        struct.unpack('B', s.read())[0] is 0x72):

                    tempdata = []
                    for i in range(17):
                        # for i in range(len(self.rawData)):
                        data2 = data[(i * 2):(2 + i * 2)]
                        value, = struct.unpack('h', data2)
                        tempdata.append(value)

                    if q.empty():
                        q.put(tempdata)
                    else:
                        q.get()
                        q.task_done()
                        q.put(tempdata)


        except:
            print("fck")
            print(s.read())


s = serial.Serial('/dev/cu.MECE653-DevB', 115200, timeout=1)
time.sleep(1)
q = queue.Queue(maxsize=10)
thread = Thread(target=get_serial_data, args=(s,))
thread.start()

# Set up sensors
numCalibrationPoints = 500
gyroScaleFactor = 131.0
accScaleFactor = 16384.0
VCC = 4.98
Resistor = 5100.0
tau = 0.98


data = Sensors(gyroScaleFactor, accScaleFactor, VCC, Resistor, tau)
data.calibrateGyro(q, numCalibrationPoints)
# data.logData(q, 10)
#
model = Model()
model.get_training_data(q, data, 200, 4, 1)

model.plot_pca()
model.trainSVM()
model.savemodel('8x3x2500-Pi')

T = int(input("Enter how many seconds to run real time control: "))
startTime = time.time()

while(time.time() < startTime + T):
    data.getData(q)
    pred = model.predict(data.force)
    print(pred, " ", q.qsize())

# filename = r"C:\Users\Rico\OneDrive\Documents\School\MecE 653\GestureControlledRoboticArm_MecE653\data\8x3x10000-V1"
# model = pickle.load(open(filename, 'rb'))
# model.plot_pca()
