import pymongo
import os
from dotenv import load_dotenv
from enum import Enum
from utils import utils

load_dotenv()

client = pymongo.MongoClient(os.getenv('CONNECTION_STRING'))

attendance_db = client.Attendance
students = attendance_db.Students
teachers = attendance_db.Teachers
classes = attendance_db.Classes

people = client.People.PeopleTypes

#---------------------------------------GENERAL FUNCTIONS-----------------------------------#
def get_person_name(id):
	person = people.find_one({"_id" : id})
	return person["name"]
	

def get_id_type(id):
	record = people.find_one({"_id" : id})
	
	if not record:
		return "Invalid"
	else:
		return record["type"]
#---------------------------------------LIBRARY FUNCTIONS-----------------------------------#

#---------------------------------------SHOP FUNCTIONS-----------------------------------#	
		
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
	students.update_one(
							{"_id" : id},
							{'$inc': {'classes_held': increment}}
						)
						
	
	
