import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522

reader = SimpleMFRC522()

not_found = "NF"

def scan_rfid_id():
    while True:
        id, name = reader.read()

        if not id:
            return not_found
        else:
            return str(id)
        
        
def scan_rfid_name():
    while True:
        id, name = reader.read()

        if not name:
            return not_found
        else:
            return name
