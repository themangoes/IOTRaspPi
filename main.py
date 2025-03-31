import lcd_display as lcd
import rfid_scanner as rfid
import mongo_cloudconnect as cloud
from buzzersounds import *
import time
from datetime import date
from utils import *
import Class


default_lcd_message = "Waiting for a\nclass to start.."
curr_lcd_message = ""
redisplay = True
mode = CLASS
curr_class = None


def main():
    global redisplay
    global curr_class
    global default_lcd_message
    global curr_lcd_message
    global mode
    
    while True:
        if mode == CLASS:
            
            if not curr_class or curr_class.status == ENDED or curr_class.status == CANCELLED:
                curr_class = Class.Current_Class()
            
            if curr_class.status == INPROGRESS:
                curr_class.is_time_up()
                
                if redisplay:
                    lcd.display_message(curr_lcd_message)
                    redisplay = False
            
                id = rfid.scan_rfid_id()
                type = cloud.get_id_type(id)
                
                if type == TEACHER and id == curr_class.faculty_id:
                    curr_class.end()
                    redisplay = True
                    if not curr_class.status == INPROGRESS:
                        exit()
                    
                elif type == TEACHER:
                    lcd.display_message("Please wait for\nclass to end.")
                    redisplay = True
                    please_wait_sound()
                    time.sleep(5)
                    
                elif type == STUDENT:
                    curr_class.add_student_attendance(id)
                    redisplay = True
                    
                elif id == rfid.not_found:
                    pass
                    
                else:
                    lcd.display_message("Invalid ID!")
                    invalid_id_sound()
                    redisplay = True
                    time.sleep(1)
                    
                    
            elif curr_class.status == NOTSTARTED:
                if redisplay:
                    lcd.display_message(default_lcd_message)
                    redisplay = False
                
                id = rfid.scan_rfid_id()
                type = cloud.get_id_type(id)
                
                if type == TEACHER:
                    curr_lcd_message = curr_class.start(id);
                    redisplay = True
                    
                elif type == STUDENT:
                    lcd.display_message("Please wait for\nclass to start.")
                    redisplay = True
                    please_wait_sound()
                    time.sleep(3)
                    
                elif id == rfid.not_found:
                    pass
    
                else:
                    lcd.display_message("Invalid ID!")
                    invalid_id_sound()
                    redisplay = True
                    time.sleep(1)
            
            
        """elif mode == LIBRARY:
            # to do library stuff
        
        elif mode == CANTEEN:
            # to do canteen stuff"""
            

        
main()
GPIO.cleanup()
