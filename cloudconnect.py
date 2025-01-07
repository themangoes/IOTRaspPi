import boto3

dynamodb = boto3.resource('dynamodb')
client = boto3.client('dynamodb')

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
				student_id,
				student_class_number,  
				teacher_id,
				teacher_class_number, 
				attending_time, 
				class_start_time, 
				date
				):
	attendance_table.put_item(
						Item = {
								"student_id" : student_id,
								"student_class_number" : student_class_number,
								"teacher_id" : teacher_id,	
								"teacher_class_number" : teacher_class_number,
								"attending_time" : attending_time,
								"class_start_time" : class_start_time,
								"date" : date,
								}
							)
	

def get_id_type(id):
	for student in student_ids:
		if student["id"] == id:
			return student_type
	
	for teacher in teacher_ids:
		if teacher["id"] == id:
			return teacher_type
			
	return invalid_type
	
	
def increment_classes_attended_count(id, increment):
	students_table.update_item(
							Key = {"id" : id},
							UpdateExpression = "SET classes_attended = classes_attended + :val",
							ExpressionAttributeValues={
									':val': increment,
								}
							)
						
						
def increment_classes_held_count(id, increment):
	teachers_table.update_item(
							Key = {"id" : id},
							UpdateExpression = "SET classes_held = classes_held + :val",
							ExpressionAttributeValues={
									':val': increment,
								}
							)
						

