# Realtime Force Myography
Using the gesture controlled robotic arm developed at [HACKED2019](https://github.com/MarkSherstan/HACKED2019) the project advanced to optimize a force myography (FMG) sensor and algorithm package that can be used to robustly control upper limb prosthetics in real time.

## Background
Although there are many multifunctional hands available for prosthesis use, commercial devices are unable to utilize them largely due to restricted control interfaces. Recent research has focused on improving pattern recognition algorithms to decode electromyographic signals (EMG) into multi degree of freedom movements to enable more robust control. Although results are promising in laboratory conditions, this technique has been unable to be transferred into commercial devices. This is largely due to current surface mounted EMG sensors having inherent unpredictable issues that affect the algorithm’s performance such as cross-talk, electrical interference, muscle fatigue effects, perspiration effects, and skin impedance. An alternative to this technology for use in prosthetics is force myography (FMG). This technology seeks to exploit the deformation resulting from residual muscle movement to obtain prosthesis control. This is typically done in a very similar manner to EMG; however, instead of measuring electrical activity, an array of pressure sensors wrapped around the user’s arm measures muscle deformation. The measured sensor values act as inputs into a pattern recognition algorithm to predict the desired motions from the user. An FMG sensor and algorithm package was designed and optimized to implement robust, real time control of a simulated prosthetic device. Two iterations of prototyping have been achieved, with the second design resulting in a wireless, low profile wristband containing 11 force sensitive resistors (FSR) sensors and an inertial measurement unit (IMU) capable of sampling up to 200 Hz.

## Photos
### Wireless Armband with 11 FSR's, IMU, and Custom PCB
<p align="center">
<img src="http://drive.google.com/uc?export=view&id=1KKZ-naMlGv-Uk4ZygPfTOd8ZeIyFCYf7" width="400"
</p>

### Coordinate Frame on Arm
<p align="center">
<img src="http://drive.google.com/uc?export=view&id=149MKG4X1k0UCgc4PwvB6nbT2mkZvo82j" width="400"
</p>

### Gestures
<p align="center">
<img src="http://drive.google.com/uc?export=view&id=1DuGyXvSHCnRzEGKyqSN79mMTX-fGARdN" width="500"
</p>

### Raw Signals (Left Time Series - Right Spectral Series)
<p align="center">
<img src="http://drive.google.com/uc?export=view&id=17V_r22DsgYIbs7M2uvsQCfZ4mAvaMt4k" width="600"
</p>

### Classified Signals PCA Representation 
<p align="center">
<img src="http://drive.google.com/uc?export=view&id=1jVfV8d97-oSygKIahRfgksKcG8Nk5u0I" width="400"
</p>
