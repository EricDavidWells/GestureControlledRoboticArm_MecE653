import matplotlib.pyplot as plt
import numpy as np
import serial
import time
import struct
import copy
import math



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
        # Check for header bytes and then read bytearray if header satisfied
        if (struct.unpack('B', self.serialConnection.read())[0] is 0x9F) and (struct.unpack('B', self.serialConnection.read())[0] is 0x6E):
            self.rawData = self.serialConnection.read(self.numSignals * self.dataNumBytes)

            # Copy raw data to new variable and set up the data out variable
            privateData = copy.deepcopy(self.rawData[:])
            dataOut = []

            # Loop through all the signals and decode the values to decimal
            for ii in range(self.numSignals):
                data = privateData[(ii*self.dataNumBytes):(self.dataNumBytes + ii*self.dataNumBytes)]
                value, = struct.unpack(self.dataType, data)
                dataOut.append(value)

        # Check if data is usable otherwise repeat (recursive function)
        try:
            if dataOut:
                return dataOut
        except:
            return self.getSerialData()

    def close(self):
        # Close the serial port connection
        self.serialConnection.close()
        print('Disconnected...')



class IMU:
    def __init__(self, gyroScaleFactor, accScaleFactor):
        # Class / object / constructor setup
        self.gyroScaleFactor = gyroScaleFactor
        self.accScaleFactor = accScaleFactor

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

    def getRawIMUvalues(self, s):
        # Get raw values from IMU from serial connection
        val = s.getSerialData()
        self.gx = val[0]
        self.gy = val[1]
        self.gz = val[2]
        self.ax = val[3]
        self.ay = val[4]
        self.az = val[5]

    def calibrateGyro(self, s, N):
        # Display message
        print("Calibrating gyro with " + str(N) + " points. Do not move!")

        # Take N readings for each coordinate and add to itself
        for ii in range(N):
            self.getRawIMUvalues(s)
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

    def processIMUvalues(self,s):
        # Get raw data
        self.getRawIMUvalues(s)

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

    def compFilter(self, s, tau):
        # Get the processed values from IMU
        self.processIMUvalues(s)

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
        self.roll = (tau)*(self.roll - self.gy*dt) + (1-tau)*(accRoll)
        self.pitch = (tau)*(self.pitch + self.gx*dt) + (1-tau)*(accPitch)



def main():
    # Set up serial connection
    portName = '/dev/cu.wchusbserial1410'
    baudRate = 115200
    dataNumBytes = 2
    numSignals = 6

    s = DAQ(portName, baudRate, dataNumBytes, numSignals)
    s.readSerialStart()

    # Set up IMU processing
    numCalibrationPoints = 500
    gyroScaleFactor = 131.0
    accScaleFactor = 16384.0
    tau = 0.98

    imu = IMU(gyroScaleFactor, accScaleFactor)
    imu.calibrateGyro(s, numCalibrationPoints)

    # Start timer and store data in array
    startTime = time.time()
    t = []
    rollArray = []
    pitchArray = []
    yawArray = []

    # Run for __ seconds
    while(time.time() < (startTime + 7)):
        imu.compFilter(s, 0.98)
        print(imu.roll, imu.pitch, imu.yaw)

        t.append(time.time() - startTime)
        rollArray.append(imu.roll)
        pitchArray.append(imu.pitch)
        yawArray.append(imu.yaw)

    # Plot data
    plt.plot(t,rollArray,'-r',linewidth=1,label='Roll')
    plt.plot(t,pitchArray,'-g',linewidth=1,label='Pitch')
    plt.plot(t,yawArray,'-b',linewidth=1,label='Yaw')

    plt.xlabel('Time (s)')
    plt.ylabel('Angle (deg)')
    plt.legend(loc='upper left')
    plt.gcf().autofmt_xdate()
    plt.show()

    # Close serial connection
    s.close()



if __name__ == '__main__':
    main()
