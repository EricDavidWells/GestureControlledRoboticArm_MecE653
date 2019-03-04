from sklearn.decomposition import PCA
from sklearn import svm
import csv
import os
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits import mplot3d
import serial
import time

def read_csv(filename):
    """
    reads csv file into a list of floats
    """

    with open(filename, 'r') as csvfile:
        reader = csv.reader(csvfile)
        data = []
        for row in reader:
            val = [float(x) for x in row]
            data.append(val)

    return data


def data_split(data, p):
    """
    splits data into training and testing data by percentage p.
    :param data: ndarray of total data to be split
    :param p: percentage of data to be used for training
    :return: data split into training and testing
    """
    datashuff = np.array(data)

    np.random.shuffle(datashuff)

    cutoff = int(p*data.shape[0])
    Xtrain = datashuff[0:cutoff, 0:-1]
    Ytrain = datashuff[0:cutoff, -1]

    Xtest = datashuff[cutoff::, 0:-1]
    Ytest = datashuff[cutoff::, -1]

    return Xtrain, Ytrain, Xtest, Ytest


def plot_pca(X, Y):
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

    return ax, pca.explained_variance_ratio_


def realtime(ser, model, t):
    """
    Realtime control of robot arm connected to serial port, continuously sends 's' character to recieve one line of
    data poitns from arduino, makes prediction using model and sends prediction to arduino

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


# read in data
print("Reading in Data: ")
datafilename = "1450_RicoGrandFinalPrez.csv"
os.chdir("..")
datafilepath = os.path.abspath(os.curdir) + "\\data\\" + datafilename
data = read_csv(datafilepath)
data = np.array(data)

print("Visualizing Data: ")
# split data into inputs and outputs
[X, Y, _, _] = data_split(data, 1)

# visualize data with PCA
plt.figure(1)
pca_ax, var = plot_pca(X, Y)
plt.show()

print("Training Model: ")
# split data into train and test
[Xtrain, Ytrain, Xtest, Ytest] = data_split(data, 0.8)

# train model
model = svm.SVC(kernel='rbf', gamma='scale')
model.fit(Xtrain, Ytrain)
print("model accuracy: ", model.score(Xtest, Ytest))

print("Connecting to Serial: ")
# connect to serial
ser = serial.Serial('COM6', 115200)
time.sleep(3)

print("Starting RealTime Control: ")
# run real time control
realtime(ser, model, 5)

ser.close()
