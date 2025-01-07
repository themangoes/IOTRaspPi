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
end_class_scans = 1
redisplay = True


def main():
    global redisplay
    while True:
        if class_in_progress:
            if is_class_time_up():
                end_class()
            if redisplay:
                lcd.display_message(curr_lcd_message)
                redisplay = False
            
            id = rfid.scan_rfid_id()
            type = cloud.get_id_type(id)
            
            if type == cloud.teacher_type and id == curr_class_faculty_id:
                end_class()
                if not class_in_progress:
                    exit()
                
            elif type == cloud.teacher_type:
                lcd.display_message("Please wait for\nclass to end.")
                please_wait_sound()
                time.sleep(5)
                
            elif type == cloud.student_type:
                add_student_attendance(id, cloud.get_student_attribute(id, "name"))
                
            elif id == rfid.not_found:
                pass
                
            else:
                lcd.display_message("Invalid ID!")
                invalid_id_sound()
                time.sleep(1)
                
        elif not class_in_progress:
            if redisplay:
                lcd.display_message(default_lcd_message)
                redisplay = False
            
            id = rfid.scan_rfid_id()
            type = cloud.get_id_type(id)
            
            if type == cloud.teacher_type:
                start_class(id, cloud.get_teacher_attribute(id, "name"))
                
            elif type == cloud.student_type:
                lcd.display_message("Please wait for\nclass to start.")
                please_wait_sound()
                time.sleep(5)
                
            elif id == rfid.not_found:
                pass

            else:
                lcd.display_message("Invalid ID!")
                invalid_id_sound()
                time.sleep(1)
            
    
def start_class(id, name):
    global class_in_progress
    global curr_class_faculty_id
    global curr_lcd_message
    global curr_class_number
    global curr_class_start_time
    global redisplay
        
    class_in_progress = True
    curr_class_faculty_id = id
    curr_class_number = cloud.get_teacher_attribute(id, "classes_held") + 1
    curr_class_start_time = time.time()
    start_time = time.strftime(
                 "%H:%M",
                 time.localtime()
                 )
    curr_lcd_message = "Faculty: " + name + "\nStartTime: " + start_time
    lcd.display_message(curr_lcd_message)
    start_class_sound()
    redisplay = True
    time.sleep(5)

        
def end_class():
    global class_in_progress 
    global end_class_scans
    global redisplay
    
    if end_class_scans < 2:
        lcd.display_message("Scan again\nto end class.")
        end_class_scans += 1
        please_wait_sound()
        time.sleep(1)
    else:
        lcd.display_message("Class ended.")
        end_class_scans = 1
        class_in_progress = False
        cloud.increment_classes_held_count(curr_class_faculty_id, 1)
        end_class_sound()
        time.sleep(2)
    
    redisplay = True


def add_student_attendance(id, name):
    global redisplay
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
                        id,
                        student_attending_class_number, 
                        curr_class_faculty_id,
                        curr_class_number, 
                        attending_time,
                        curr_class_start_time,
                        datenow
                        )
    cloud.increment_classes_attended_count(id, 1)
    student_attending_sound()
    redisplay = True
    time.sleep(2)


def is_class_time_up():
    if not class_in_progress:
        return False
        
    time_now = time.time()
    timediff = time_now - curr_class_start_time
    if timediff >= 3600:
        return True
    
        
main()
GPIO.cleanup()
