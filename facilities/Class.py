import time
# import ..IOTRaspPi.utils.lcd_display as lcd
from cloud import mongo_cloudconnect as cloud
from utils import lcd_display as lcd
from utils import utils
from utils import buzzersounds as sounds


class_time_limit = 3600
cancel_class_time_limit = 1


class Current_Class:
	class_sl_num = cloud.new_class_sl_num()
	status = utils.NOTSTARTED
	faculty_id = 0
	start_time_epoch = 0
	start_time_fstr = ""
	start_date = ""
	teacher_class_number = -1
	end_class_scans = 0
	attending_students_set = {"None"};
	
	
	def start(self, id):
		self.status = utils.INPROGRESS
		self.faculty_id = id
		name = cloud.get_person_name(id)
		self.class_number = cloud.get_teacher_attribute(id, "classes_held") + 1
		self.start_time_epoch = time.time()
		self.start_time_fstr = utils.get_time_now()
		self.start_date = utils.get_date_now()
		cloud.put_attendance(
							self.class_sl_num,
							self.faculty_id,
							self.class_number, 
							self.start_time_fstr,
							"class in progress",
							self.start_date,
							list(self.attending_students_set),
							self.status
							)
		lcd.display_message("Faculty: " + name + "\nStartTime: " + self.start_time_fstr)
		sounds.start_class_sound()
		print("Class SL Num = ",self.class_sl_num)
		time.sleep(3)
		return ("Faculty: " + name + "\nStartTime: " + self.start_time_fstr)
	
	
	def add_student_attendance(self, id):
		if id in self.attending_students_set:
			return
    
		name = cloud.get_person_name(id)
		if "None" in self.attending_students_set:
			self.attending_students_set.remove("None")
			
		self.attending_students_set.add(id)
		
		cloud.put_attendance(
							self.class_sl_num,
							self.faculty_id,
							self.teacher_class_number, 
							self.start_time_fstr,
							"class in progress",
							self.start_date,
							list(self.attending_students_set),
							self.status
							)
		lcd.display_message(name[:10] + "..." + " is\nattending.")
		sounds.student_attending_sound()
		time.sleep(2)
		return (name[:10] + "..." + " is\nattending.")
		
	
	def end(self):
		if self.get_time_diff() <= cancel_class_time_limit:
			self.cancel_class()
			return
		
		if self.end_class_scans < 1:
			lcd.display_message("Scan again\nto end class.")
			self.end_class_scans += 1
			sounds.please_wait_sound()
			time.sleep(1)
		else:
			self.status = utils.ENDED
			cloud.put_attendance(
							self.class_sl_num,
							self.faculty_id,
							self.class_number, 
							self.start_time_fstr,
							utils.get_time_now(),
							self.start_date,
							list(self.attending_students_set),
							self.status
							)
			lcd.display_message("Class ended.")
			self.end_class_scans = 0
			self.attending_students_set.clear()
			self.attending_students_set.add("None")
			cloud.increment_classes_held_count(self.faculty_id, 1)
			for id in self.attending_students_set:
				cloud.increment_classes_attended_count(id, self.faculty_id, 1)
			sounds.end_class_sound()
			time.sleep(2)
			
		
	def cancel_class(self):
		if self.end_class_scans < 1:
			lcd.display_message("Scan again to\ncancel class.")
			self.end_class_scans += 1
			sounds.please_wait_sound()
			time.sleep(1)
		else:
			self.status = utils.CANCELLED
			cloud.delete_class(self.class_sl_num)
			lcd.display_message("Class cancelled.")
			self.end_class_scans = 0
			self.attending_students_set.clear()
			self.attending_students_set.add("None")
			sounds.end_class_sound()
			time.sleep(3)
			
		
	def is_time_up(self):
		if self.status is utils.NOTSTARTED:
			return False
        
		timediff = self.get_time_diff()
		if timediff >= class_time_limit:
			self.end_class()
			return True
		else:
			return False
			
	
	def get_time_diff(self):
		return time.time() - self.start_time_epoch
