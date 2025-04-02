import time


NOTAPPLICABLE = "N/A"

CLASS = "class"
LIBRARY = "library"
SHOP = "shop"
MODES = [CLASS, LIBRARY, SHOP]

STUDENT = "student"
TEACHER = "teacher"
LIBRARIAN = "librarian"
ADMIN = "admin"
PEOPLETYPES = [STUDENT, TEACHER, LIBRARIAN, ADMIN]

BOOK = "book"
ITEM = "item"

NOTSTARTED = "Not Started"
INPROGRESS = "In Progress"
ENDED = "Ended"
CANCELLED = "Cancelled"
CLASSSTATUS = [NOTSTARTED, INPROGRESS, ENDED, CANCELLED]

AVAILABLE = "available"
BORROWED = "borrowed"
RETURNED = "returned"

BORROWING = "borrowing"
RETURNING = "returning"
NONE = "none"


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
    
