import RPi.GPIO as GPIO
from time import sleep

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

buzzer1_pinnum = 2
buzzer2_pinnum = 3

GPIO.setup(buzzer1_pinnum, GPIO.OUT)
GPIO.setup(buzzer2_pinnum, GPIO.OUT)

myfreq = 1100

buzz1 = GPIO.PWM(buzzer1_pinnum, myfreq)
buzz2 = GPIO.PWM(buzzer2_pinnum, myfreq)



def play_for_and_stop_for_with_freq(playtime, stoptime, freq):
	buzz1.ChangeFrequency(freq)
	buzz2.ChangeFrequency(freq)
	buzz1.start(50)
	buzz2.start(50)
	sleep(playtime)
	
	buzz1.stop()
	buzz2.stop()
	sleep(stoptime)


def start_class_sound():
	play_for_and_stop_for_with_freq(0.1, 0.05, myfreq)
	play_for_and_stop_for_with_freq(0.1, 0.1, myfreq)
	play_for_and_stop_for_with_freq(0.1, 0.05, myfreq)
	play_for_and_stop_for_with_freq(0.1, 0.2, myfreq)
	play_for_and_stop_for_with_freq(0.15, 0, myfreq)
	
	
def end_class_sound():
	play_for_and_stop_for_with_freq(0.1, 0.15, myfreq)
	play_for_and_stop_for_with_freq(0.3, 0.2, myfreq)
	play_for_and_stop_for_with_freq(0.1, 0, myfreq)
	

def student_attending_sound():
	play_for_and_stop_for_with_freq(0.1, 0.05, myfreq)
	play_for_and_stop_for_with_freq(0.1, 0, myfreq)
	
	
def invalid_id_sound():
	play_for_and_stop_for_with_freq(0.1, 0.05, myfreq)
	play_for_and_stop_for_with_freq(0.05, 0.05, myfreq)
	play_for_and_stop_for_with_freq(0.05, 0.05, myfreq)
	play_for_and_stop_for_with_freq(0.05, 0.05, myfreq)
	play_for_and_stop_for_with_freq(0.2, 0, myfreq)
	

def please_wait_sound():
	play_for_and_stop_for_with_freq(0.4, 0, myfreq)
	
	

#----------------------------------------------------------------
# All sounds
#----------------------------------------------------------------
#start_class_sound()
#end_class_sound()
#student_attending_sound()
#invalid_id_sound()
#please_wait_sound()
#----------------------------------------------------------------
