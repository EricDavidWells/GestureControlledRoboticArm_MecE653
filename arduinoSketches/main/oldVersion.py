import numpy as np
import serial
import time
import struct
import copy
import math
import pandas as pd


class DAQ:
    def __init__(self, serialPort, serialBaud, dataNumBytes, numSignals):
        # Class / object / constructor setup
        self.port = serialPort
        self.baud = serialBaud
        self.dataNumBytes = dataNumBytes
        self.numSignals = numSignals
        self.rawData = bytearray(numSignals * dataNumBytes)
        self.dataType = None

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
        # Pause and clear buffer to start with a good connection
        time.sleep(2)
        self.serialConnection.reset_input_buffer()

    def getSerialData(self):
        dataOut = []

        # Check for header bytes and then read bytearray if header satisfied
        if (struct.unpack('B', self.serialConnection.read())[0] is 0x9F) and (struct.unpack('B', self.serialConnection.read())[0] is 0x6E):
            self.rawData = self.serialConnection.read(self.numSignals * self.dataNumBytes)

            # Copy raw data to new variable and set up the data out variable
            privateData = copy.deepcopy(self.rawData[:])

            # Loop through all the signals and decode the values to decimal
            for i in range(self.numSignals):
                data = privateData[(i*self.dataNumBytes):(self.dataNumBytes + i*self.dataNumBytes)]
                value, = struct.unpack(self.dataType, data)
                dataOut.append(value)

        # Check if data is usable otherwise repeat (recursive function)
        if dataOut:
            if (struct.unpack('B', self.serialConnection.read())[0] is 0xAE) and (struct.unpack('B', self.serialConnection.read())[0] is 0x72):
                return dataOut
            else:
                return self.getSerialData()
        else:
            return self.getSerialData()

    def close(self):
        # Close the serial port connection
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
        val = s.getSerialData()
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



def main():
    # Set up serial connection
    # portName = '/dev/cu.MECE653-DevB' # /dev/cu.MECE653-DevB
    portName = 'COM7'
    baudRate = 115200
    dataNumBytes = 2
    numSignals = 17

    s = DAQ(portName, baudRate, dataNumBytes, numSignals)
    s.readSerialStart()

    # Set up sensors
    numCalibrationPoints = 500
    gyroScaleFactor = 131.0
    accScaleFactor = 16384.0
    VCC = 4.98
    Resistor = 5100.0
    tau = 0.98

    data = Sensors(gyroScaleFactor, accScaleFactor, VCC, Resistor, tau)
    data.calibrateGyro(s, numCalibrationPoints)

    # Run for __ seconds
    startTime = time.time()
    count = 0
    tempData = []

    while(time.time() < (startTime + 14)):
        data.getData(s)

        tempData.append(data.force + [data.roll, data.pitch, data.yaw])

        print(time.time()-startTime)
        print("Roll/Pitch/Yaw: ", round(data.roll,2), round(data.pitch,2), round(data.yaw,2))
        print("FSR's: ", [round(x,2) for x in data.force])
        print()

        count += 1

    print("Average sample rate: ", int(count / (time.time() - startTime)), " Hz")

    # Close serial connection
    s.close()

    # Write data to CSV
    df = pd.DataFrame(tempData, columns=['FSR1', 'FSR2', 'FSR3', 'FSR4', 'FSR5',
                                         'FSR6', 'FSR7', 'FSR8', 'FSR9', 'FSR10',
                                         'FSR11', 'Avg', 'Roll', 'Pitch', 'Yaw'])
    df.to_csv('data.csv', index=None, header=True)


if __name__ == '__main__':
    main()
