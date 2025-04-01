import utils.lcd_display as lcd
import utils.rfid_scanner as rfid
from utils.buzzersounds import *
import time
from datetime import date
from utils.utils import *
import facilities.Class as Class
import facilities.Class as Library
import cloud.mongo_cloudconnect as cloud


curr_lcd_message = ""
redisplay = True
mode = CLASS
curr_class = None
library = None


def main():
    global redisplay
    global curr_class
    global default_lcd_message
    global curr_lcd_message
    global mode
    
    while True:
        
#--------------------------------CLASS MODE----------------------------------------#        
        
        if mode == CLASS:
            
            if not curr_class or curr_class.status == ENDED or curr_class.status == CANCELLED:
                curr_class = Class.Current_Class()
                curr_lcd_message = "Waiting for a\nclass to start.."
                redisplay = True
            
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
                    #if not curr_class.status == INPROGRESS:
                        #exit()
                    
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
                    curr_lcd_message = "Waiting for a\nclass to start.."
                    lcd.display_message(curr_lcd_message)
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
                    
            
#--------------------------------LIBRARY MODE----------------------------------------#
            
        elif mode == LIBRARY:
            if not library:
                library = Library.Library()
                
            if not library.is_open:
                if redisplay:
                    curr_lcd_message = "Library is\nclosed."
                    lcd.display_message(curr_lcd_message)
                    redisplay = False
                
                id = rfid.scan_rfid_id()
                type = cloud.get_id_type(id)
                
                if type == LIBRARIAN:
                    library.open()
                    curr_lcd_message = "Library is open,\nWelcome!"
                    
                elif id == rfid.not_found:
                    pass
                    
                elif type in PEOPLETYPES:
                    lcd.display_message = "Please wait for\nLibrary to open."
                    redisplay = True
                    please_wait_sound()
                    time.sleep(3)
                
                else:
                    print("Invalid ID!")
                    invalid_id_sound()
                    redisplay = True
                    time.sleep(1)
                
                
            elif library.is_open:
                 if redisplay:
                    lcd.display_message(curr_lcd_message)
                    redisplay = False
                
                id = rfid.scan_rfid_id()
                type = cloud.get_id_type(id)
                
                if type == LIBRARIAN:
                    library.close()
                    redisplay=True
                
                elif type in PEOPLETYPES and library.status == NONE:
                    library.open_escrow("borrow")
                    
                elif type in PEOPLETYPES and library.status == BORROWING:
                    if not library.curr_borrower_id == id:
                        lcd.display_message("Please wait for\nprev user to end")
                        please_wait_sound()
                        redisplay = True
                        time.sleep(2)
                    library.close_escrow()
                    library.borrow_escrow()
                    
                elif type in PEOPLETYPES and library.status == RETURNING:
                    library.close_escrow()
                    library.return_escrow()
                
                elif type == BOOK:
                    if library.status == BORROWING or library.status == RETURNING:
                        library.add_to_escrow(id)
                    elif cloud.is_borrowed(id):
                        library.set_to_returning()
                        library.open_escrow("return")
                        library.add_to_escrow(id)
                    else:
                        lcd.display_message("Scan your card\nfirst.")
                        redisplay = True
                        invalid_id_sound()
                        time.sleep(2)
                    
                elif id == rfid.not_found:
                    pass
                
                else:
                    print("Invalid ID!")
                    invalid_id_sound()
                    redisplay = True
                    time.sleep(1)
                    
                    
#--------------------------------SHOP MODE----------------------------------------#        
        
        elif mode == SHOP:
            print("do shop stuff")
            # to do shop stuff
            

        
main()
GPIO.cleanup()
