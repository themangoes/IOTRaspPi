import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522
from lcd_display import display_message
from time import sleep

reader = SimpleMFRC522()

not_found = "NF"


def scan_rfid_id():
        rfid, id = reader.read_no_block()
        
        if not id:
            return not_found
        else:
            return id.strip()
            
            

if __name__ == '__main__':
    while True:
        sleep(3)
        id = scan_rfid_id()
        display_message(id)
    
