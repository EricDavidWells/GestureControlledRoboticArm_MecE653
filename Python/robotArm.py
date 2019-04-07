import RPi.GPIO as GPIO

class robotArm:
    def __init__(self):
        self.joint1Range = [500,2300]
        self.joint2Range = [1000,2000]
        self.joint3Range = [500,1200]
        self.joint4Range = [1100,1100]   # [800,1800]

    def startControl(self):
        # Run `pinout` to see the numbers
        GPIO.setmode(GPIO.BOARD)

        # Set up PWM pins on GPIO
        GPIO.setup(12, GPIO.OUT)
        GPIO.setup(13, GPIO.OUT)
        GPIO.setup(18, GPIO.OUT)
        GPIO.setup(19, GPIO.OUT)

        # Initialize all servos to center position
        self.joint1 = GPIO.PWM(12, 50)
        self.joint2 = GPIO.PWM(13, 50)
        self.joint3 = GPIO.PWM(18, 50)
        self.joint4 = GPIO.PWM(19, 50)

        # Write start position
        self.joint1.start(7.5)
        self.joint2.start(7.5)
        self.joint3.start(7.5)
        self.joint4.start(7.5)

    def updateState(self, state):
        # percentage / (20 ms * unit conversion)
        dutyCycleScale = 100 / (20*1000)

        # Check the different states and write a pule
        if state == 1:
            # Fist
            self.joint4.ChangeDutyCycle(self.joint4Range[1]*dutyCycleScale)
        elif state == 2:
            # Rest
            self.joint4.ChangeDutyCycle(self.joint4Range[0]*dutyCycleScale)
        elif state == 3:
            # Extension
            self.joint1.ChangeDutyCycle(self.joint1Range[0]*dutyCycleScale)
        elif state == 4:
            # Flexion
            self.joint1.ChangeDutyCycle(self.joint1Range[1]*dutyCycleScale)
        elif state == 5:
            # Forward
            self.joint2.ChangeDutyCycle(self.joint2Range[0]*dutyCycleScale)
            self.joint3.ChangeDutyCycle(self.joint3Range[1]*dutyCycleScale)
        elif state == 6:
            # Back
            self.joint2.ChangeDutyCycle(self.joint2Range[1]*dutyCycleScale)
            self.joint3.ChangeDutyCycle(self.joint3Range[0]*dutyCycleScale)
        else:
            print("No state found")

    def endControl(self):
        # Stop writing PWM signal to servos
        self.joint1.stop()
        self.joint2.stop()
        self.joint3.stop()
        self.joint4.stop()

        # Clean up ports used
        GPIO.cleanup()


def main():
    bot = robotArm()
    bot.startControl()

    while True:
        state = input('Enter State: ')
        try:
            state = int(state)
            if state == -1:
                break

            bot.updateState(state)
        except:
            print("oops")

    bot.endControl()


if __name__ == '__main__':
    main()
