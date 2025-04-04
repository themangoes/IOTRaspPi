import pymongo
import os
from dotenv import load_dotenv
from enum import Enum
from utils import utils
import time

load_dotenv()

client = pymongo.MongoClient(os.getenv('CONNECTION_STRING'))

attendance_db = client.Attendance
students = attendance_db.Students
teachers = attendance_db.Teachers
classes = attendance_db.Classes

library_db = client.Library
books = library_db.Books
borrow_history = library_db.Borrow_History

shop_db = client.Shop
items = shop_db.Items
transactions = shop_db.Transaction_History

people = client.People.PeopleTypes

#---------------------------------------GENERAL FUNCTIONS-----------------------------------#
def get_person_name(id):
	person = people.find_one({"_id" : id})
	return person["name"]
	
	
def get_person_attribute(id, attribute):
	person = people.find_one({"_id" : id})
	return person[attribute]
	

def get_id_type(id):
	
	record = people.find_one({"_id" : id})
	
	if not record:
		record = books.find_one({"_id" : id})
		if not record:
			record = items.find_one({"_id" : id})
			if not record:
				return "Invalid"
			else:
				return utils.ITEM
		else:
			return utils.BOOK
	else:
		return record["type"]
		
		
def process_transaction(id, fee, type):
	person_record = people.find_one({"_id" : id})
	pre_balance = person_record["balance"]
	if type == "loss":
		post_balance = pre_balance - fee
	elif type == "gain":
		post_balance = pre_balance + fee
	if post_balance < 0:
		return False
	else:
		people.update_one({"_id":id}, {"$set" : {"balance" : post_balance}})
		return True
	
	
#---------------------------------------LIBRARY FUNCTIONS-----------------------------------#

def new_borrow_sl_num():
	sl_num_record = borrow_history.find_one({"_id":0})
	new_sl_num = sl_num_record["prev_borrow_sl_num"] + 1
	borrow_history.update_one({"_id":0}, {'$inc': {'prev_borrow_sl_num': 1}})
	return new_sl_num
	
	
def get_book_attribute(id, attribute):
	book_record = books.find_one({"_id":id})
	return book_record[attribute]


def is_borrowed(id):
	book_record = books.find_one({"_id":id})
	if book_record["status"] == utils.AVAILABLE:
		return False
	else:
		return True


def borrow_books(borrower_id, escrow, borrow_date, return_due_date, due_date_epoch):
	status = utils.BORROWED
	returned_date = utils.NOTAPPLICABLE
	late_fee_payed = 0
	borrowed = 0
	for book_id in escrow:
		sl_num = new_borrow_sl_num()
		title = get_book_attribute(book_id, "title")
		set_book_data(
						book_id, 
						borrower_id, 
						borrow_date, 
						returned_date,
						return_due_date, 
						due_date_epoch, 
						status, 
						sl_num
					)
					
		borrower_name = get_person_name(borrower_id)
		add_to_borrow_history(
								sl_num,
								book_id,
								title,
								borrower_id,
								borrower_name,
								borrow_date,
								returned_date,
								return_due_date,
								due_date_epoch,
								status,
								late_fee_payed
							)
		borrowed += 1
		
	people.update_one(
						{"_id":borrower_id}, {"$inc" : {"borrowed_books_qty":borrowed}}
					)
	
							
	
def set_book_data(book_id, borrower_id, borrow_date, returned_date, return_due_date, due_date_epoch, status, sl_num):	
	books.update_one(
						{"_id":book_id}, {'$set' : {
						"_id":book_id,
						"status" : status,
						"borrower_id" : borrower_id,
						"borrowed_date" : borrow_date,
						"returned_date" : returned_date,
						"due_date" : return_due_date,
						"due_epoch_time" : due_date_epoch,
						"borrow_sl_num" : sl_num
						}}, upsert=True
					)
	
	
def return_books(borrower_id, escrow):
	return_date = utils.get_date_now()
	status = utils.RETURNED
	return_error_books = set()
	returned = 0

	for book_id in escrow:
		sl_num = get_book_attribute(book_id, "borrow_sl_num")
		due_date_epoch = get_book_attribute(book_id, "due_epoch_time")
		late_fee = ((time.time() - due_date_epoch) / 86400)		
		transact = True
		if late_fee > 0:
			late_fee = int(late_fee) + 1
			transact = process_transaction(borrower_id, late_fee, "loss")
		else:
			late_fee = 0
			
		if transact:
			borrow_history.update_one(
										{"_id":sl_num}, {"$set": {
										"returned_date":return_date,
										"status":status,
										"late_fee_payed" : late_fee
										}}
									)
			set_book_data(
							book_id,
							utils.NOTAPPLICABLE,
							utils.NOTAPPLICABLE,
							utils.NOTAPPLICABLE,
							utils.NOTAPPLICABLE,
							0,
							utils.AVAILABLE,
							0
						)
			returned -= 1
		else:
			return_error_books.add(book_id)
			
	people.update_one(
						{"_id":borrower_id}, {"$inc" : {"borrowed_books_qty":returned}}
					)
	return return_error_books
	
	
def add_to_borrow_history(sl_num, book_id, title, borrower_id, borrower_name, borrow_date, returned_date, return_due_date, due_date_epoch, status, late_fee_payed):
	borrow_history.update_one(
								{"_id":sl_num}, {"$set": {
								"sl_num":sl_num,
								"book_id":book_id,
								"title":title,
								"borrower_id":borrower_id,
								"borrower_name":borrower_name,
								"borrow_date":borrow_date,
								"returned_date":returned_date,
								"return_due_date":return_due_date,
								"due_date_epoch":due_date_epoch,
								"status":status,
								"late_fee_payed":late_fee_payed
								}}, upsert=True
							)
	
	
def get_late_fee(book_id):
	due_date_epoch = get_book_attribute(book_id, "due_epoch_time")
	late_fee = ((time.time() - due_date_epoch) / 86400)	
	if late_fee > 0:
		late_fee = int(late_fee) + 1
		return late_fee
	else:
		return 0


#---------------------------------------SHOP FUNCTIONS-----------------------------------#	

def new_transaction_sl_num():
	sl_num_record = transactions.find_one({"_id":0})
	new_sl_num = sl_num_record["prev_transaction_sl_num"] + 1
	transactions.update_one({"_id":0}, {'$inc': {'prev_transaction_sl_num': 1}})
	return new_sl_num
	

def get_item_attribute(id, attribute):
	item = items.find_one({"_id" : id})
	info = item[attribute]
	return info
	
	
def buy_items(buyer_id, escrow):
	error_items = []
	for item_id in escrow:
		sl_num = new_transaction_sl_num()
		buy_date = utils.get_date_now()
		buy_time = utils.get_time_now()
		item_name = get_item_attribute(item_id, "item")
		item_price = get_item_attribute(item_id, "price")
		buyer_name = get_person_name(buyer_id)
		
		transact = process_transaction(buyer_id, item_price, "loss")
		
		if transact:
			add_to_transaction_history(
										sl_num,
										item_id,
										item_name,
										item_price,
										buyer_id,
										buyer_name,
										buy_date,
										buy_time,
										"loss"
									)
		else:
			error_items.append(item_id)	
	
	return error_items
	

def add_to_transaction_history(sl_num, item_id, item_name, item_price, buyer_id, buyer_name, buy_date, buy_time, type):
	transactions.update_one(
							{"_id":sl_num}, {"$set" : {
							"sl_num" : sl_num,
							"item_id" : item_id,
							"item_name" : item_name,
							"item_price" : item_price,
							"buyer_id" : buyer_id,
							"buyer_name" : buyer_name,
							"buy_date" : buy_date,
							"buy_time" : buy_time,
							"type" : type
							}}, upsert=True
						)
	
#-------------------------------CLASS ATTENDANCE FUNCTIONS-----------------------------------------#
def new_class_sl_num():
	sl_num_record = classes.find_one({"_id":0})
	new_sl_num = sl_num_record["prev_class_sl_num"] + 1
	classes.update_one({"_id":0}, {'$inc': {'prev_class_sl_num': 1}})
	return new_sl_num


def get_teacher_attribute(id, attribute):
	teacher_item = teachers.find_one({"_id" : id})
	info = teacher_item[attribute]
	return info


def get_student_attribute(id, attribute):
	student_item = students.find_one({"_id" : id})
	info = student_item[attribute]
	return info


def put_attendance(
				sl_num,
				teacher_id,
				teacher_class_number, 
				class_start_time, 
				class_end_time,
				date,
				attending_students_set,
				status
				):
	return classes.update_one({"_id" : sl_num}, {'$set' : {
								"_id" : sl_num,
								"teacher_id" : teacher_id,	
								"class_number" : teacher_class_number,
								"class_start_time" : class_start_time,
								"class_end_time" : class_end_time,
								"date" : date,
								"attending_students" : attending_students_set,
								"status" : status
								}}, upsert=True
							)
							
							
def delete_class(sl_num):
	print("Trying to delete Class : ",sl_num)
	return classes.delete_one({"_id" : sl_num})
	

def increment_classes_attended_count(student_id, teacher_id, increment):
	students.update_one(
							{"_id" : student_id},
							{'$inc': {f'classes_attended.{teacher_id}': increment}}
						)
						
						
def increment_classes_held_count(id, increment):
	teachers.update_one(
							{"_id" : id},
							{'$inc': {'classes_held': increment}}
						)
						
	
	
