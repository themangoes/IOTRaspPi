from utils import buzzersounds as sounds
from utils import lcd_display as lcd
from utils import utils
from cloud import mongo_cloudconnect as cloud
import time


escrow_timeout_limit = 180
due_date_time_sec = 604800


class Shop():
	is_open = False
	is_shopping = False
	is_escrow_open = False
	curr_shopper_id = None
	escrow = []
	escrow_open_time = None
	escrow_price = 0
	make_new = False
	
	
	def open(self):
		self.is_open = True
		
		
	def close(self):
		self.is_open = False
		self.make_new = True
		if self.is_escrow_open:
			self.delete_escrow_instance()
			
	
	def set_curr_shopper(self, id):
		self.curr_shopper_id = id
		
		
	def open_escrow(self):
		if self.is_escrow_open:
			return
			
		self.is_shopping = True
		self.escrow_open_time = time.time()
		self.is_escrow_open = True
		
		
	def close_escrow(self):
		if not self.is_escrow_open:
			return	
		
		self.delete_escrow_instance()
		
		
	def add_to_escrow(self, id):
		if not self.is_escrow_open:
			return
		
		self.escrow.append(id)
		self.escrow_price += cloud.get_item_attribute(id, "price")
		return f"Buying: {len(self.escrow)}\nTotal:{self.escrow_price}Rs"
		
		
	def buy_escrow(self):
		if len(self.escrow) <= 0:
			lcd.display_message("Your Cart is\nEmpty!")
			sounds.please_wait_sound()
			time.sleep(2)
			return
			
		error_items = cloud.buy_items(
							self.curr_shopper_id, 
							self.escrow,
							)
		if len(error_items) > 0:
			sounds.invalid_id_sound()
			lcd.display_message(f"No funds to\nbuy {len(error_items)} items")
			time.sleep(3)
		self.delete_escrow_instance()
		self.close_escrow()
	
		
	def is_escrow_timeout(self):
		if time.time() - self.escrow_open_time >= escrow_timeout_limit:
			self.close_escrow()
			return True
		else:
			return False	
		
		
	def delete_escrow_instance(self):
		self.escrow.clear()
		escrow_open_time = None
		self.is_escrow_open = False
		self.is_shopping = False
		self.curr_borrower_id = None
			
