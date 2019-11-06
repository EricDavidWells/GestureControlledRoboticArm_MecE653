import numpy as np
from biosppy.signals import emg

signal = np.loadtxt('./examples/emg.txt')
out = emg.emg(signal=signal, sampling_rate = 1000, show=True)