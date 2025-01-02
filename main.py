import lcd_display as lcd
import rfid_scanner as rfid
import cloudconnect as cloud
from buzzersounds import *
import time
from datetime import date

default_lcd_message = "Waiting for a\nclass to start.."
curr_lcd_message = ""
class_in_progress = False
curr_class_faculty_id = 0
curr_class_start_time = ""
curr_class_number = -1

def main():
    while True:
        if class_in_progress:
            lcd.display_message(curr_lcd_message)
            
            id = rfid.scan_rfid_id()
            type = cloud.get_id_type(id)
            
            if type == cloud.teacher_type and id == curr_class_faculty_id:
                end_class()
                exit()
                
            elif type == cloud.teacher_type:
                lcd.display_message("Please wait for\nclass to end.")
                please_wait_sound()
                time.sleep(5)
                
            elif type == cloud.student_type:
                add_student_attendance(id, cloud.get_student_attribute(id, "name"))
                
            else:
                lcd.display_message("Invalid ID!")
                invalid_id_sound()
                time.sleep(2)
                
        elif not class_in_progress:
            lcd.display_message(default_lcd_message)
            
            id = rfid.scan_rfid_id()
            type = cloud.get_id_type(id)
            
            if type == cloud.teacher_type:
                start_class(id, cloud.get_teacher_attribute(id, "name"))
                
            elif type == cloud.student_type:
                lcd.display_message("Please wait for\nclass to start.")
                please_wait_sound()
                time.sleep(5)
                
            else:
                lcd.display_message("Invalid ID!")
                invalid_id_sound()
                time.sleep(2)
            
    
def start_class(id, name):
    global class_in_progress
    global curr_class_faculty_id
    global curr_lcd_message
    global curr_class_number
    global curr_class_start_time
        
    class_in_progress = True
    curr_class_faculty_id = id
    cur_class_number = cloud.get_new_class_number(id)
    curr_class_start_time = time.strftime(
                 "%H:%M",
                 time.localtime()
                 )
    curr_lcd_message = "Faculty: " + name + "\nStartTime: " + curr_class_start_time
    lcd.display_message(curr_lcd_message)
    start_class_sound()
    time.sleep(5)

        
def end_class():
    global class_in_progress 
    lcd.display_message("Class ended.")
    class_in_progress = False
    end_class_sound()
    time.sleep(2)


def add_student_attendance(id, name):
    lcd.display_message(name + " is\nattending.")
    attending_time = time.strftime(
                        "%H:%M",
                        time.localtime()
                        )
    datenow = time.strftime(
                        "%D",
                        time.localtime()
                        )
    student_attending_class_number = cloud.get_student_attribute(id, "classes_attended") + 1
    
    cloud.put_attendance(
                        student_attending_class_number, 
                        curr_class_number, 
                        curr_class_faculty_id,
                        id,
                        attending_time,
                        curr_class_start_time,
                        datenow
                        )
    student_attending_sound()
    time.sleep(2)


main()
GPIO.cleanup()
