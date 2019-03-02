from sklearn import svm
from sklearn.decomposition import PCA
import csv
import os
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits import mplot3d

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


datafilename = "1450_RicoGrandFinalPrez.csv"
os.chdir("..")
datafilepath = os.path.abspath(os.curdir) + "\\data\\" + datafilename

data = read_csv(datafilepath)
data = np.array(data)
[Xtrain, Ytrain, Xtest, Ytest] = data_split(data, 0.8)

plt.figure(1)
pca_ax, var = plot_pca(Xtrain, Ytrain)

plt.show()