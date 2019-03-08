from sklearn.decomposition import PCA
from sklearn import svm
import csv
import os
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits import mplot3d
import serial
import time
import struct
import copy


def read_csv(filename):
    """
    reads csv file into a list of floats
    """

    print("Reading in Data: ")
    with open(filename, 'r') as csvfile:
        reader = csv.reader(csvfile)
        data = []
        for row in reader:
            val = [float(x) for x in row]
            data.append(val)

    return data


def data_split(X, Y, p):
    """
    splits data into training and testing data by percentage p.
    :param data: ndarray of total data to be split
    :param p: percentage of data to be used for training
    :return: data split into training and testing
    """

    print("Visualizing Data: ")

    data = np.hstack((X, np.transpose(np.array([Y]))))
    datashuff = np.array(data)
    np.random.shuffle(datashuff)

    cutoff = int(p*data.shape[0])
    Xtrain = datashuff[0:cutoff, 0:-1]
    Ytrain = datashuff[0:cutoff, -1]

    Xtest = datashuff[cutoff::, 0:-1]
    Ytest = datashuff[cutoff::, -1]

    return Xtrain, Ytrain, Xtest, Ytest


def plot_pca(X, Y, show=True):
    """
    Plots the 3 dimensional PCA reduced version of data X.  Y is used to change color of different labels.
    :param X: ndarray of input data without labels
    :param Y: ndarray of labels with rows aligning with X
    :return: pyplot axis of PCA reduced data
    """
    pca = PCA(n_components=3)
    pca.fit(X)
    Xpca = pca.fit_transform(X)

    ax = plt.axes(projection='3d')
    for i in range(0, int(Y.max())+1):
        Xtemp = Xpca[Y==i]
        ax.scatter3D(Xtemp[:, 0], Xtemp[:, 1], Xtemp[:, 2], cmap='Greens')

    if show is True:
        plt.figure(1)
        plt.show()

    return ax, pca.explained_variance_ratio_


def handshake_serial(ser, model, t):
    """
    Realtime control of robot arm connected to serial port using handshake protocol, continuously sends 's' character
    to recieve one line of data poitns from arduino, makes prediction using model and sends prediction to arduino

    :param ser: serial port object
    :param model: model used for prediction, must have a .predict method
    :param t: time in seconds to stay in realtime control
    """
    starttime = time.time()
    ser.write('+\n'.encode())

    counter = 0
    while time.time()-starttime < t:
        ser.write('s\n'.encode())
        line = ser.readline()
        line = line.decode()
        line = line.replace('\n', '')
        line = line.replace('\r', '')
        line = line.split(',')
        data = [float(x) for x in line[0:-1]]

        pred = model.predict([data])
        ser.write(('y'+str(pred)+'\n').encode())

        print(data)
        counter += 1

    ser.write('-\n'.encode())


def get_training_data(s, n, classnum, trainnum):
    s.readSerialStart()
    xdata = []
    ydata = []
    counter = 0
    for i in range(0, trainnum):
        input("training iteration: {0}".format(i))
        for k in range(0, classnum):
            input("class number: {0}".format(k))
            for j in range(0, n):
                data = s.getSerialData()
                xdata.append(data)
                ydata.append(k)
                if counter > 50:
                    print('.')
                    counter = 0
                counter += 1
    return np.array(xdata), np.array(ydata)


def realtime_prediction(s, model, t, p=False):
    starttime = time.time()

    s.readSerialStart()
    counter = 0
    while time.time() - starttime < t:
        data = s.getSerialData()
        if data:
            pred = model.predict([data])
            counter += 1
            print(data, counter, pred)

    if p is True:
        print('Average sample rate: {}Hz'.format(int(counter/t)))

    return pred


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

        if (struct.unpack('B', self.serialConnection.read())[0] is 0x9F) \
                and (struct.unpack('B', self.serialConnection.read())[0] is 0x6E):
        # if (int(self.serialConnection.read().hex(),16) is 159) and (int(self.serialConnection.read().hex(),16) is 110):
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
    portName = 'COM6'
    baudRate = 115200
    dataNumBytes = 2
    numSignals = 8
    dataPoints = 1000
    datafilename = "1450_RicoGrandFinalPrezMod.csv"
    os.chdir("..")
    datafilepath = os.path.abspath(os.curdir) + "\\data\\" + datafilename

    # CONNECT TO TO SERIAL
    s = serialPlot(portName, baudRate, dataNumBytes, numSignals)

    # # READ DATAFILE
    # data = read_csv(datafilepath)
    # data = np.array(data)
    # X = data[:, 0:-1]
    # Y = data[:, -1]

    # GET TRAINING DATA
    [X, Y] = get_training_data(s, 200, 2, 2)

    # VISUALIZE DATA
    pca_ax, var = plot_pca(X, Y)

    # TRAIN MODEL
    [Xtrain, Ytrain, Xtest, Ytest] = data_split(X, Y, 0.8)
    model = svm.SVC(kernel='rbf', gamma='scale')
    model.fit(Xtrain, Ytrain)
    print("model accuracy: ", model.score(Xtest, Ytest))

    # REAL TIME PREDICTION
    realtime_prediction(s, model, 5, True)

    s.close()


if __name__ == '__main__':
    main()