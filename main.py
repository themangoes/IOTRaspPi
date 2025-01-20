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
curr_class_start_time_epoch = 0
curr_class_start_time_fstr = ""
curr_class_number = -1
end_class_scans = 1
redisplay = True
attending_students_set = {"None"};


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
                redisplay = True
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
                redisplay = True
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
    global curr_class_start_time_epoch
    global curr_class_start_time_fstr
    global redisplay
        
    class_in_progress = True
    curr_class_faculty_id = id
    curr_class_number = cloud.get_teacher_attribute(id, "classes_held") + 1
    curr_class_start_time_epoch = time.time()
    curr_class_start_time_fstr = time.strftime(
                 "%H:%M",
                 time.localtime()
                 )
    curr_lcd_message = "Faculty: " + name + "\nStartTime: " + curr_class_start_time_fstr
    lcd.display_message(curr_lcd_message)
    start_class_sound()
    redisplay = True
    cloud.put_attendance(
                        curr_class_faculty_id,
                        curr_class_number, 
                        curr_class_start_time_fstr,
                        "class in progress",
                        get_date_now(),
                        attending_students_set
                        )
    time.sleep(5)

        
def end_class():
    global class_in_progress 
    global end_class_scans
    global redisplay
    global attending_students_set
    
    if end_class_scans < 2:
        lcd.display_message("Scan again\nto end class.")
        end_class_scans += 1
        please_wait_sound()
        time.sleep(1)
    else:
        lcd.display_message("Class ended.")
        cloud.put_attendance(
                        curr_class_faculty_id,
                        curr_class_number, 
                        curr_class_start_time_fstr,
                        get_time_now(),
                        get_date_now(),
                        attending_students_set
                        )
        end_class_scans = 1
        class_in_progress = False
        attending_students_set.clear()
        attending_students_set.add("None")
        cloud.increment_classes_held_count(curr_class_faculty_id, 1)
        end_class_sound()
        time.sleep(2)
    
    redisplay = True


def add_student_attendance(id, name):
    global redisplay
    global attending_students_set
    
    if id in attending_students_set:
        return;
    
    lcd.display_message(name + " is\nattending.")
    student_attending_class_number = cloud.get_student_attribute(id, "classes_attended") + 1
    if "None" in attending_students_set:
        attending_students_set.remove("None")
    attending_students_set.add(id)
    cloud.put_attendance(
                        curr_class_faculty_id,
                        curr_class_number, 
                        curr_class_start_time_fstr,
                        "class in progress",
                        get_date_now(),
                        attending_students_set
                        )
    cloud.increment_classes_attended_count(id, 1)
    student_attending_sound()
    redisplay = True
    time.sleep(2)


def is_class_time_up():
    if not class_in_progress:
        return False
        
    time_now = time.time()
    timediff = time_now - curr_class_start_time_epoch
    if timediff >= 3600:
        return True


def get_date_now():
    datenow = time.strftime(
                        "%d/%m/%y",
                        time.localtime()
                        )
    return datenow


def get_time_now():
    timenow = time.strftime(
                        "%H:%M",
                        time.localtime()
                        )
    return timenow
        
main()
GPIO.cleanup()
