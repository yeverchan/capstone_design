import Jetson.GPIO as GPIO
import time


class Motor_Module:
    def __init__(self, IN1, IN2, MOTOR1, MOTOR2):
        self.IN1 = IN1
        self.IN2 = IN2
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(self.IN1, GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup(self.IN2, GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup(MOTOR1, GPIO.OUT)
        self.servo1 = GPIO.PWM(MOTOR1, 50)  # pin 32 servo1
        GPIO.setup(MOTOR2, GPIO.OUT)
        self.servo2 = GPIO.PWM(MOTOR2, 50)  # pin 33 servo2
    
    def move_two_motors(self, degree1, degree2):
        self.servo1.start(0)
        self.servo2.start(0)
        self.servo1.ChangeDutyCycle(degree1)  # 2 / 5
        time.sleep(0.5)
        self.servo1.ChangeDutyCycle(0)
        self.servo2.ChangeDutyCycle(degree2)  # 12 / 10
        time.sleep(0.5)
        self.servo2.ChangeDutyCycle(0)
        self.servo1.stop()
        self.servo2.stop()

    def move_one_motor(self):
        GPIO.output(self.IN1, GPIO.HIGH)
        GPIO.output(self.IN2, GPIO.LOW)
        time.sleep(1)

        GPIO.output(self.IN1, GPIO.LOW)
        GPIO.output(self.IN2, GPIO.HIGH)
        time.sleep(1)


if __name__ == '__main__':
    MM = Motor_Module(26, 24, 32, 33)
    MM.move_two_motors(2, 12)  # reset
    MM.move_two_motors(2, 10)  # plastic
    MM.move_two_motors(2, 12)  # paper
    MM.move_two_motors(5, 12)  # can
    MM.move_two_motors(2, 12)  # reset
    MM.move_one_motor()
    GPIO.cleanup()
