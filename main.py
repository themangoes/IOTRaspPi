import lcd_display as lcd
import rfid_scanner as rfid
import check_ids
import time

default_lcd_message = "Waiting for a\nclass to start.."
class_in_progress = False
curr_class_faculty_id = 0

def main():
    while True:
        lcd.display_message(default_lcd_message)
        #time.sleep(3)
        id = rfid.scan_rfid_id()
        name = rfid.scan_rfid_name()
        if id == rfid.not_found or name == rfid.not_found:
            lcd.display_message("Please scan\nagain.")
            #rfid.scan_again()
        
        person_type = check_ids.check_type(id)
        
        if (person_type == check_ids.teacher_type):
            start_class(id, name)
        elif (person_type == check_ids.student_type):
            add_attendance_to_student(id, name)
        else:
            invalid_rfid_card()
            
        
def init():
    check_ids.init()
    
    
    
def start_class(id, name):
    global class_in_progress
    if class_in_progress:
        #end_class(id, name)
        class_in_progress = False
        return
        
    class_in_progress = True
    curr_class_faculty_id = id
    faculty_name = str(name)
    start_time = time.strftime(
                 "%H:%M",
                 time.localtime()
                 )

    lcd.display_message("Faculty: " + name + "\nStartTime: " + start_time)
    time.sleep(3)
        
        

    
init()
main()
