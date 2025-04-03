from utils import buzzersounds as sounds
from utils import lcd_display as lcd
from utils import utils
from cloud import mongo_cloudconnect as cloud
import time


escrow_timeout_limit = 60
due_date_time_sec = 604800
borrow_qty_limit = 1


class Library():
	is_open = False
	status = utils.NONE
	is_escrow_open = False
	curr_borrower_id = None
	curr_borrower_borrowed_qty = 0
	escrow = set()
	escrow_open_time = None
	total_late_fee = 0
	make_new = False
	
	
	def open(self):
		self.is_open = True
		
		
	def close(self):
		self.is_open = False
		self.make_new = True
		if self.is_escrow_open:
			self.delete_escrow_instance()
			
	
	def set_curr_borrower(self, id):
		self.curr_borrower_id = id
		self.curr_borrower_borrowed_qty = cloud.get_person_attribute(id, "borrowed_books_qty")
		
		
	def open_escrow(self, mode):
		if self.is_escrow_open:
			return
			
		self.status = mode
		self.escrow_open_time = time.time()
		self.is_escrow_open = True
		
		
	def close_escrow(self):
		if not self.is_escrow_open:
			return	
		
		self.delete_escrow_instance()
		
		
	def add_to_escrow(self, id):
		if not self.is_escrow_open:
			return
		
		if self.status == utils.BORROWING and borrow_qty_limit - self.curr_borrower_borrowed_qty - len(self.escrow) <= 0:
			lcd.display_message("Borrow limit\nreached!")
			sounds.invalid_id_sound()
			time.sleep(3)
			self.close_escrow()
			return "Library is open,\nWelcome!"

		self.escrow.add(id)
		if self.status == utils.RETURNING:
			if not self.check_if_return_escrow_is_valid():
				lcd.display_message("Invalid\nEscrow!")
				sounds.invalid_id_sound()
				time.sleep(2)
				return "Library is open,\nWelcome!"
		
		if self.status == utils.BORROWING:
			if cloud.get_book_attribute(id, "status") == utils.BORROWED:
				lcd.display_message("This book is\nborrowed.")
				sounds.invalid_id_sound()
				time.sleep(2)
				self.close_escrow()
				return "Library is open,\nWelcome!"
			due_date_epoch = time.time() + due_date_time_sec
			return_due_date = time.strftime(
            	            "%d/%m/%y",
                	        time.localtime(due_date_epoch)
                    	    )
			return f"Borrowing: {len(self.escrow)}\nDue:{return_due_date}"
			
		elif self.status == utils.RETURNING:
			self.total_late_fee += cloud.get_late_fee(id)
			return f"Returning: {len(self.escrow)}\nLate Fee:{self.total_late_fee}Rs"
		
		
	def borrow_escrow(self):
		if len(self.escrow) <= 0:
			lcd.display_message("Your Escrow is\nEmpty!")
			sounds.please_wait_sound()
			time.sleep(2)
			return
			
		borrow_date = utils.get_date_now()
		due_date_epoch = time.time() + due_date_time_sec
		return_due_date = time.strftime(
                        "%d/%m/%y",
                        time.localtime(due_date_epoch)
                        )
		cloud.borrow_books(
							self.curr_borrower_id, 
							self.escrow,
							borrow_date,
							return_due_date,
							due_date_epoch
							)
		self.delete_escrow_instance()
		self.close_escrow()
		
		
	def return_escrow(self, id):
		self.curr_borrower_id = id
		if not self.check_if_return_escrow_is_valid():
			print("Invalid Escrow")
			return

		error_books = cloud.return_books(
							self.curr_borrower_id, 
							self.escrow,
							)
		if len(error_books) > 0:
			sounds.invalid_id_sound()
			lcd.display_message(f"No funds to\nreturn {len(error_books)} books")
			time.sleep(3)
		self.delete_escrow_instance()
		self.close_escrow()
	
	
	def check_if_return_escrow_is_valid(self):
		borrower_id = None
		first_iteration = True
		for book_id in self.escrow:
			if self.curr_borrower_id and borrower_id:
				if not self.curr_borrower_id == borrower_id:
					lcd.display_message("You didnt borrow\nthis book")
					sounds.invalid_id_sound()
					time.sleep(2)
					self.delete_escrow_instance()
					self.close_escrow()
					return False
				
			if not cloud.is_borrowed(book_id):
				lcd.display("Book not\nborrowed!")
				sounds.invalid_id_sound()
				time.sleep(2)
				self.delete_escrow_instance()
				self.close_escrow()
				return False
			if first_iteration:
				borrower_id = cloud.get_book_attribute(book_id, "borrower_id")
				first_iteration = False
			elif not borrower_id == cloud.get_book_attribute(book_id, "borrower_id"):
				lcd.display_message("Book borrowers\ndiffer!")
				sounds.invalid_id_sound()
				time.sleep(2)
				self.delete_escrow_instance()
				self.close_escrow()
				return False
		time.sleep(2)
		return True
		
		
	def set_to_borrowing(self):
		self.status = utils.BORROWING
		
		
	def set_to_returning(self):
		self.status = utils.RETURNING
		
		
	def is_escrow_timeout(self):
		if time.time() - self.escrow_open_time >= escrow_timeout_limit:
			self.close_escrow()
			return True
		else:
			return False	
		
		
	def delete_escrow_instance(self):
		self.escrow.clear()
		self.total_late_fee = 0
		escrow_open_time = None
		self.is_escrow_open = False
		self.status = utils.NONE
		self.curr_borrower_id = None
			
