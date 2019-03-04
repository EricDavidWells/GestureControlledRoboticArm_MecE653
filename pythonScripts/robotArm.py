import RPi.GPIO as GPIO
import time

# Run `pinout` to see the numbers
GPIO.setmode(GPIO.BOARD)

# Set up PWM pis from GPIO and define initial position. Ensure there is a common
# ground shared with the power supply.
GPIO.setup(12, GPIO.OUT)
p = GPIO.PWM(12, 100)
p.start(11.5)

GPIO.setup(13, GPIO.OUT)
q = GPIO.PWM(13, 100)
q.start(11.5)

GPIO.setup(18, GPIO.OUT)
r = GPIO.PWM(18, 100)
r.start(11.5)

GPIO.setup(19, GPIO.OUT)
s = GPIO.PWM(19, 100)
s.start(11.5)

# Functions for moving each of the four DOF's on robotic arm
def updateAngleP(angle):
        duty = (float(angle) / 10.0) + 2.5
        p.ChangeDutyCycle(duty)

def updateAngleQ(angle):
        duty = (float(angle) / 10.0) + 2.5
        q.ChangeDutyCycle(duty)

def updateAngleR(angle):
        duty = (float(angle) / 10.0) + 2.5
        r.ChangeDutyCycle(duty)

def updateAngleS(angle):
        duty = (float(angle) / 10.0) + 2.5
        s.ChangeDutyCycle(duty)

# Main loop running until broken
try:
    while True:
        angleP = input("Angle P: ")
        angleQ = input("Angle Q: ")
        angleR = input("Angle R: ")
        angleS = input("Angle S: ")
        print
        updateAngleP(angleP)
        updateAngleQ(angleQ)
        updateAngleR(angleR)
        updateAngleS(angleS)
        time.sleep(1)

except KeyboardInterrupt:
    p.stop()
    q.stop()
    r.stop()
    s.stop()
    GPIO.cleanup()
