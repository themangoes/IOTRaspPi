import boto3

dynamodb = boto3.resource('dynamodb')

students_table = dynamodb.Table("students")
teachers_table = dynamodb.Table("teachers")
attendance_table = dynamodb.Table("attendance")

student_ids = students_table.scan(AttributesToGet = ["id"])["Items"]
teacher_ids = teachers_table.scan(AttributesToGet = ["id"])["Items"]

teacher_type = 0
student_type = 1
invalid_type = -1


def get_teacher_attribute(id, attribute):
	try:
		teacher_item = teachers_table.get_item(Key = {"id" : id})
		info = teacher_item["Item"][attribute]
		return info
	except KeyError:
		return "NF"


def get_student_attribute(id, attribute):
	try:
		student_item = students_table.get_item(Key = {"id" : id})
		info = student_item["Item"][attribute]
		return info
	except KeyError:
		return "NF"


def put_attendance(
				student_class_number, 
				teacher_class_number, 
				teacher_id, 
				student_id, 
				attending_time, 
				class_start_time, 
				date
				):
	attendance_table.put_item(
						Item = {
								"student_class_number" : student_class_number,
								"teacher_class_number" : teacher_class_number,
								"teacher_id" : teacher_id,
								"student_id" : student_id,
								"attending_time" : attending_time,
								"class_start_time" : class_start_time,
								"date" : date,
								}
							)


def get_new_class_number(teacher_id):
	classes_held = teachers_table.get_item(Key = {"id" : teacher_id},
											AttributesToGet = ["classes_held"]
										)["Item"]["classes_held"]
	return classes_held + 1
	

def get_id_type(id):
	for student in student_ids:
		#print("input= " + id + " | rowid= " + student["id"])
		if student["id"] == id:
			return student_type
	
	for teacher in teacher_ids:
		#print("input= " + id + " | rowid= " + teacher["id"])
		if teacher["id"] == id:
			return teacher_type
			
	return invalid_type
