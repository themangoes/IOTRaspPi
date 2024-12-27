import RPi.GPIO as GPIO
from time import sleep

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

buzzer1_pinnum = 2
buzzer2_pinnum = 3

GPIO.setup(buzzer1_pinnum, GPIO.OUT)
GPIO.setup(buzzer2_pinnum, GPIO.OUT)

buzz1 = GPIO.PWM(buzzer1_pinnum, 3100)
buzz2 = GPIO.PWM(buzzer2_pinnum, 3100)


def play_for_and_stop_for(playtime, stoptime):
	buzz1.ChangeFrequency(3100)
	buzz2.ChangeFrequency(3100)
	buzz1.start(50)
	buzz2.start(50)
	sleep(playtime)
	
	buzz1.stop()
	buzz2.stop()
	sleep(stoptime)


def start_class_sound():
	play_for_and_stop_for(0.1, 0.05)
	play_for_and_stop_for(0.1, 0.1)
	play_for_and_stop_for(0.1, 0.05)
	play_for_and_stop_for(0.1, 0.2)
	play_for_and_stop_for(0.15, 0.00001)
	

