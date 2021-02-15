from gpiozero import Servo
from time import sleep


SERVO_MIN = 0.000544
SERVO_MAX = 0.0024


def get_servos():
    servo_nico = Servo(18, min_pulse_width=SERVO_MIN,
                       max_pulse_width=SERVO_MAX)
    servo_finn = Servo(13, min_pulse_width=SERVO_MIN,
                       max_pulse_width=SERVO_MAX)
    return servo_nico, servo_finn


while True:
    nico, finn = get_servos()
    nico.min()
    finn.min()
    sleep(1)
    nico.close()
    finn.close()
    sleep(2)
    nico, finn = get_servos()
    nico.max()
    finn.max()
    sleep(1)
    nico.close()
    finn.close()
    sleep(2)
