from gpiozero import Servo
from time import sleep


servo = Servo(18, min_pulse_width=.000544, max_pulse_width=.0024)
servo_two = Servo(13, min_pulse_width=.000554, max_pulse_width=0.0024)
while True:
    servo.min()
    servo_two.min()
    sleep(1)
    sleep(1)
    servo.max()
    servo_two.max()
    sleep(1)
    sleep(1)
