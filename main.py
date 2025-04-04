import utils.lcd_display as lcd
import utils.rfid_scanner as rfid
from utils.buzzersounds import *
import time
from datetime import date
from utils.utils import *
import facilities.Class as Class
import facilities.Library as Library
import facilities.Shop as Shop
import cloud.mongo_cloudconnect as cloud


curr_lcd_message = ""
redisplay = True
mode = LIBRARY
curr_class = None
library = None
shop = None


def main():
    global redisplay
    global curr_class
    global library
    global shop
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
                    time.sleep(2)
                    
            
#--------------------------------LIBRARY MODE----------------------------------------#
            
        elif mode == LIBRARY:
            if not library or library.make_new:
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
                    lcd.display_message(curr_lcd_message)
                    redisplay = True
                    start_class_sound()
                    time.sleep(5)
                    
                elif id == rfid.not_found:
                    pass
                    
                elif type in PEOPLETYPES or type == BOOK:
                    curr_lcd_message = "Please wait for\nLibrary to open."
                    lcd.display_message(curr_lcd_message)
                    redisplay = True
                    please_wait_sound()
                    time.sleep(3)
                
                else:
                    print("Invalid ID!")
                    invalid_id_sound()
                    redisplay = True
                    time.sleep(1)
                
                
            elif library.is_open:
                if not library.is_escrow_open:
                    curr_lcd_message = "Library is open,\nWelcome!"
                    
                if redisplay:
                    lcd.display_message(curr_lcd_message)
                    redisplay = False
                
                id = rfid.scan_rfid_id()
                type = cloud.get_id_type(id)
                
                if type == LIBRARIAN:
                    library.close()
                    curr_lcd_message = "Library is\nclosed."
                    lcd.display_message(curr_lcd_message)
                    redisplay=True
                    end_class_sound()
                    time.sleep(5)
                
                elif type in PEOPLETYPES and library.status == NONE:
                    library.open_escrow(BORROWING)
                    lcd.display_message("Scan chosen\nbooks.")
                    redisplay = False
                    library.set_curr_borrower(id)
                    please_wait_sound()
                    time.sleep(3)
                    
                elif type in PEOPLETYPES and library.status == BORROWING:
                    if not library.curr_borrower_id == id:
                        lcd.display_message("Please wait for\nprev user to end")
                        please_wait_sound()
                        redisplay = True
                        time.sleep(2)
                    lcd.display_message("Borrowing...")
                    library.borrow_escrow()
                    library.close_escrow()
                    lcd.display_message("Return the books\non time!")
                    please_wait_sound()
                    time.sleep(3)
                    curr_lcd_message = "Library is open,\nWelcome!"
                    redisplay = True
                    
                elif type in PEOPLETYPES and library.status == RETURNING:
                    lcd.display_message("Returning...")
                    library.return_escrow(id)
                    library.close_escrow()
                    lcd.display_message("Thank You!")
                    please_wait_sound()
                    time.sleep(3)
                    curr_lcd_message = "Library is open,\nWelcome!"
                    redisplay = True
                
                elif type == BOOK:
                    lcd.display_message("Scanning...")
                    if id in library.escrow:
                        lcd.display_message("Already scanned!")
                        please_wait_sound()
                        redisplay = True
                    
                    elif library.status == BORROWING:
                        curr_lcd_message = library.add_to_escrow(id)
                        lcd.display_message(curr_lcd_message)
                        student_attending_sound()
                        redisplay = True
                        
                    elif cloud.is_borrowed(id):
                        library.set_to_returning()
                        library.open_escrow(RETURNING)
                        curr_lcd_message = library.add_to_escrow(id)
                        lcd.display_message(curr_lcd_message)
                        student_attending_sound()
                        redisplay = True
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
                    time.sleep(2)
                    
                if not library.status == NONE:
                    if library.is_escrow_timeout():
                        lcd.display_message("Time Limit\nExceeded!")
                        invalid_id_sound()
                        time.sleep(2)
                        curr_lcd_message = "Library is open,\nWelcome!"
                        redisplay = True
                    
                    
#--------------------------------SHOP MODE----------------------------------------#        
        
        elif mode == SHOP:
            if not shop or shop.make_new:
                shop = Shop.Shop()
                
            if not shop.is_open:
                if redisplay:
                    curr_lcd_message = "Shop is closed."
                    lcd.display_message(curr_lcd_message)
                    redisplay = False
                
                id = rfid.scan_rfid_id()
                type = cloud.get_id_type(id)
                
                if type == SHOPKEEPER:
                    shop.open()
                    curr_lcd_message = "Shop is open,\nWelcome!"
                    lcd.display_message(curr_lcd_message)
                    redisplay = True
                    start_class_sound()
                    time.sleep(5)
                    
                elif id == rfid.not_found:
                    pass
                    
                elif type in PEOPLETYPES or type == ITEM:
                    curr_lcd_message = "Please wait for\nShop to open."
                    lcd.display_message(curr_lcd_message)
                    redisplay = True
                    please_wait_sound()
                    time.sleep(3)
                
                else:
                    print("Invalid ID!")
                    invalid_id_sound()
                    redisplay = True
                    time.sleep(1)
                
                
            elif shop.is_open:
                if not shop.is_escrow_open:
                    curr_lcd_message = "Shop is open,\nWelcome!"
                    
                if redisplay:
                    lcd.display_message(curr_lcd_message)
                    redisplay = False
                
                id = rfid.scan_rfid_id()
                type = cloud.get_id_type(id)
                
                if type == SHOPKEEPER:
                    shop.close()
                    curr_lcd_message = "Shop is closed."
                    lcd.display_message(curr_lcd_message)
                    redisplay=True
                    end_class_sound()
                    time.sleep(5)
                
                elif type in PEOPLETYPES and not shop.is_shopping:
                    shop.open_escrow()
                    lcd.display_message("Scan chosen\nitems.")
                    redisplay = False
                    shop.set_curr_shopper(id)
                    please_wait_sound()
                    time.sleep(3)
                    
                elif type in PEOPLETYPES and shop.is_shopping:
                    if not shop.curr_shopper_id == id:
                        lcd.display_message("Please wait for\nprev user to end")
                        please_wait_sound()
                        redisplay = True
                        time.sleep(2)
                    lcd.display_message("Buying...")
                    shop.buy_escrow()
                    shop.close_escrow()
                    lcd.display_message("Thank You for\nShopping!")
                    please_wait_sound()
                    time.sleep(3)
                    curr_lcd_message = "Shop is open,\nWelcome!"
                    redisplay = True
                
                elif type == ITEM:
                    lcd.display_message("Scanning...")
                    
                    if shop.is_shopping and shop.is_escrow_open:
                        curr_lcd_message = shop.add_to_escrow(id)
                        lcd.display_message(curr_lcd_message)
                        student_attending_sound()
                        redisplay = True
                    else:
                        lcd.display_message("Scan your card\nfirst.")
                        redisplay = True
                        invalid_id_sound()
                    time.sleep(3)
                    
                elif id == rfid.not_found:
                    pass
                
                else:
                    print("Invalid ID!")
                    invalid_id_sound()
                    redisplay = True
                    time.sleep(2)
                    
                if shop.is_shopping:
                    if shop.is_escrow_timeout():
                        lcd.display_message("Time Limit\nExceeded!")
                        invalid_id_sound()
                        time.sleep(2)
                        curr_lcd_message = "Shop is open,\nWelcome!"
                        redisplay = True
            

        
main()
GPIO.cleanup()
