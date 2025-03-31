import time


CLASS = "class"
LIBRARY = "library"
SHOP = "shop"

STUDENT = "student"
TEACHER = "teacher"
LIBRARIAN = "librarian"
ADMIN = "admin"

NOTSTARTED = "Not Started"
INPROGRESS = "In Progress"
ENDED = "Ended"
CANCELLED = "Cancelled"


def get_date_now():
    datenow = time.strftime(
                        "%d/%m/%y",
                        time.localtime()
                        )
    return datenow


def get_time_now():
    timenow = time.strftime(
                        "%H:%M",
                        time.localtime()
                        )
    return timenow
    
