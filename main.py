import lcd_display as lcd
import rfid_scanner as rfid
import check_ids
from buzzersounds import *
import time

default_lcd_message = "Waiting for a\nclass to start.."
curr_lcd_message = ""
class_in_progress = False
curr_class_faculty_id = 0

def main():
    while True:
        if class_in_progress:
            lcd.display_message(curr_lcd_message)
            id = rfid.scan_rfid_id()
            type = check_ids.check_type(id)
            if type == check_ids.teacher_type and id == curr_class_faculty_id:
                end_class()
                #exit()
            elif type == check_ids.teacher_type:
                lcd.display_message("Please wait for\nclass to end.")
                time.sleep(5)
            elif type == check_ids.student_type:
                add_student_attendance(id, check_ids.get_name(id, type))
            else:
                lcd.display_message("Invalid ID!")
                time.sleep(5)
                
        elif not class_in_progress:
            lcd.display_message(default_lcd_message)
            id = rfid.scan_rfid_id()
            type = check_ids.check_type(id)
            if type == check_ids.teacher_type:
                start_class(id, check_ids.get_name(id, type))
            elif type == check_ids.student_type:
                lcd.display_message("Please wait for\nclass to start.")
                time.sleep(5)
            else:
                lcd.display_message("Invalid ID!")
                time.sleep(5)
            
        
def init():
    check_ids.init()
    
    
    
def start_class(id, name):
    global class_in_progress
    global curr_class_faculty_id
    global curr_lcd_message
        
    class_in_progress = True
    curr_class_faculty_id = id
    start_time = time.strftime(
                 "%H:%M",
                 time.localtime()
                 )
    curr_lcd_message = "Faculty: " + name + "\nStartTime: " + start_time
    lcd.display_message(curr_lcd_message)
    start_class_sound()
    time.sleep(5)

        
def end_class():
    global class_in_progress 
    lcd.display_message("Class ended.")
    class_in_progress = False
    time.sleep(2)


def add_student_attendance(id, name):
    lcd.display_message(name + " is\nattending.")
    time.sleep(2)

    
init()
main()
GPIO.cleanup()
