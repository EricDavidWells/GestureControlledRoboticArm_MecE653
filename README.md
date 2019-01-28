# HACKED2019
Designed and programmed in collaboration with [Eric Wells](https://github.com/Rico5678).

## Inspiration
Gesture control is becoming a popular technique integrated into the growing area of virtual reality and rehabilitation. The popular Myo Armband achieved this using Electromyography (EMG) sensors placed on the forearm. However, this device was recently discontinued from production, leaving a gap in the marketplace.

## What it does
We achieved the same result as the Myo Armband, using a unique method involving Force Sensitive Resistors (FSR's) rather than the expensive EMG sensors. These sensors are much cheaper compared to EMG sensors. They are wrapped around the users forearm and measure pressure changes resulting from different muscle configurations. We use a desktop robotic arm in order to demonstrate the gesture control.

## How we built it
This was entirely constructed in the 24 hour time limit at the hackathon. This included:

* Hardware design and construction
* Mechanical design and construction
* Machine learning algorithm design and implementation
* Implementation of trained model onto functioning hardware
* All software involved in reading and mapping sensor data

## Challenges we ran into
* Non-repatability in the FSR sensors due to the compliant wristband used caused for many retraining sessions to be required

## Accomplishments that I'm proud of
* Successfully classify 4 different gesture controls
* Successfully control a 3 degree of freedom (DOF) robotic arm

## What I learned
How to train and design various classifiers in MATLAB, and how to export the trained model for implementation on real-time hardware.

## What's next for Gesture Controlled Desktop Robotic Arm
Cable management and a more robustly designed mechanical wristband would allow for better repeatability, and likely more classification options.

## Built With
* C++
* Arduino
* MATLAB
* hardware
* machine-learning
* SVM
* human-computer-interaction

## Classification Labels
* 0 --> relax
* 1 --> extension
* 2 --> flexion
* 3 --> fist

## Photo
![](https://github.com/MarkSherstan/HACKED2019/blob/master/data/demoImage.png)
