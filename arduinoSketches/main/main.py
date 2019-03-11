from statistics import mean
import matplotlib.pyplot as plt
import numpy as np
import serial
import time
import struct
import copy
import math



class DAQ:
    def __init__(self, serialPort, serialBaud, dataNumBytes, numSignals):
        self.port = serialPort
        self.baud = serialBaud
        self.dataNumBytes = dataNumBytes
        self.numSignals = numSignals
        self.rawData = bytearray(numSignals * dataNumBytes)
        self.dataType = None

        if dataNumBytes == 2:
            self.dataType = 'h'

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
        time.sleep(2)
        self.serialConnection.reset_input_buffer()

    def getSerialData(self):
        if (struct.unpack('B', self.serialConnection.read())[0] is 0x9F) and (struct.unpack('B', self.serialConnection.read())[0] is 0x6E):
            self.rawData = self.serialConnection.read(self.numSignals * self.dataNumBytes)

            privateData = copy.deepcopy(self.rawData[:])
            temp = []
            for i in range(self.numSignals):
                data = privateData[(i*self.dataNumBytes):(self.dataNumBytes + i*self.dataNumBytes)]
                value,  = struct.unpack(self.dataType, data)
                self.data[i].append(value)
                temp.append(value)

        try:
            if temp:
                return temp
        except:
            return self.getSerialData()

    def close(self):
        self.serialConnection.close()
        print('Disconnected...')



class Sensors:
    def __init__(self, gyroScaleFactor, accScaleFactor, VCC, Resistor, Tau):
        self.gyroScaleFactor = gyroScaleFactor
        self.accScaleFactor = accScaleFactor
        self.VCC = VCC
        self.Resistor = Resistor
        self.Tau = Tau

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
        self.force = []

    def getRawSensorValues(self, s):
        val = s.getSerialData()
        self.gx = val[0]
        self.gy = val[1]
        self.gz = val[2]
        self.ax = val[3]
        self.ay = val[4]
        self.az = val[5]
        self.FSRvalues = [val[6], val[7], val[8], val[9], val[10], val[11], val[12], val[13]]

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
        self.gx = self.gx / self.gyroScaleFactor
        self.gy = self.gy / self.gyroScaleFactor
        self.gz = self.gz / self.gyroScaleFactor

        # Convert to g force
        self.ax = self.ax / self.accScaleFactor
        self.ay = self.ay / self.accScaleFactor
        self.az = self.az / self.accScaleFactor

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
            fsrV = FSRvalues[ii] * self.VCC / 1023

            # Use voltage and static resistor value to calculate FSR resistance
            fsrR = ((self.VCC - fsrV) * self.Resistor) / fsrV

            # Guesstimate force based on slopes in figure 3 of FSR datasheet (conductance)
            fsrG = 1 / fsrR

            # Break parabolic curve down into two linear slopes
            if (fsrR <= 600):
                self.force[ii] = (fsrG - 0.00075) / 0.00000032639
            else:
                self.force[ii] =  fsrG / 0.000000642857

        # Write the last entry of force to be the average value
        self.force[8] = np.mean(force)

    def getData(self,s):
        # Get data from serial
        self.getRawSensorValues(s)

        # Process IMU values
        self.compFilter()

        # Process FSR values
        self.processFSRvalues()



def main():
    portName = '/dev/cu.wchusbserial1410'
    baudRate = 115200
    dataNumBytes = 2
    numSignals = 14

    s = DAQ(portName, baudRate, dataNumBytes, numSignals)
    s.readSerialStart()

    numCalibrationPoints = 500
    gyroScaleFactor = 65.5
    accScaleFactor = 8192
    VCC = 4.98
    Resistor = 5100
    Tau = 0.98

    data = Sensors(gyroScaleFactor, accScaleFactor, VCC, Resistor, Tau)
    data.calibrateGyro(s, numCalibrationPoints)

    for ii in range(1000):
        data.getData(s)
        print(data.roll, data.pitch, data.yaw)
        print(data.force)

    s.close()


if __name__ == '__main__':
    main()
