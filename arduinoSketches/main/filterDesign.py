from scipy.fftpack import fft
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from scipy.signal import butter, lfilter


def fftPlotter(t,signal):
    # Create Subplot
    f, (ax1, ax2) = plt.subplots(2, 1)
    f.suptitle('Time and Frequency Plots of FSR Sensor')

    # Number of sample points
    Fs = 200
    T = 1.0/Fs
    N = len(signal)

    # Plot time series data
    ax1.plot(t,signal)
    ax1.set_xlabel('Time (s)')
    ax1.set_ylabel('Force [grams]')

    # Perform FFT
    yf = fft(signal)
    xf = np.linspace(0.0, 1.0/(2.0*T), N//2)

    # Plot frequency spectrum
    ax2.plot(xf, 2.0/N * np.abs(yf[0:N//2]))
    ax2.set_xlabel('Frequency [Hz]')
    ax2.set_ylabel('Force [grams]')
    ax2.grid()

    # Display plot
    f.subplots_adjust(hspace=0.5)
    plt.show()

def plotAll(t,df):
    # Create a figure
    fig = plt.figure(figsize=(12, 6))
    ID = ['Time','FSR1','FSR2','FSR3','FSR4','FSR5','FSR6','FSR7','FSR8','FSR9','FSR10','FSR11','Avg']

    # Unwrap data and plot
    for ii in range(1, df.shape[1]):
        y = df.iloc[:, ii].tolist()
        plt.plot(t,y,label=ID[ii])

    # Format plot
    plt.xlabel('Time (s)',fontweight='bold')
    plt.ylabel('Force (grams)',fontweight='bold')
    plt.legend(loc='upper center', ncol=4)
    plt.show()

def buterLowpass(t,signal):
    # Create Subplot
    f, (ax1, ax2) = plt.subplots(2, 1)
    f.suptitle('Filtering - Butterworth')

    # Plot original data
    ax1.plot(t,signal)
    ax1.set_xlabel('Time (s)')
    ax1.set_ylabel('Force [grams]')

    # Filter properties
    order = 5
    fs = 200
    cutoff = 10
    nyq = 0.5 * fs

    # Apply filter
    b, a = butter(order, cutoff/nyq, btype='low', analog=False)
    y = lfilter(b, a, signal)

    # Plot filtered data
    ax2.plot(t,y)
    ax2.set_xlabel('Time (s)')
    ax2.set_ylabel('Force [grams]')
    plt.show()


# Read data from csv and make a data frame
df = pd.read_csv('data.csv')
t = df.iloc[:, 0].tolist()
signal = df.iloc[:, 1].tolist()

# Plot all data
# plotAll(t,df)

# Make an FFT
# fftPlotter(t,signal)

# Butterworth Filtering
buterLowpass(t,signal)
