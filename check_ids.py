import csv

id_column = 0
name_column = 1

teacher_type = 0
student_type = 1
invalid_type = -1

def init():
    global teacher_database
    global student_database
    global fieldnames
    
    teacher_database_file = open("teacherids.csv")
    teacher_database = csv.DictReader(teacher_database_file)
    
    student_database_file = open("studentids.csv")
    student_database = csv.DictReader(student_database_file)
    
    fieldnames = teacher_database.fieldnames
    

def check_type(id):
    init()
    for row in teacher_database:
        #print(row)
        if (row['id'] == id):
            return teacher_type
            
    for row in student_database:
        #print(row)
        if (row[fieldnames[id_column]] == id):
            return student_type
            
    return invalid_type
        
    
    
    
    
