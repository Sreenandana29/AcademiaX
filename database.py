import sqlite3

conn = sqlite3.connect("academiax.db")

cursor = conn.cursor()


# STUDENTS TABLE
cursor.execute("""
CREATE TABLE IF NOT EXISTS students(

student_id INTEGER PRIMARY KEY AUTOINCREMENT,

name TEXT,

usn TEXT UNIQUE,

semester INTEGER,

department TEXT

)

""")


# SUBJECTS TABLE
cursor.execute("""

CREATE TABLE IF NOT EXISTS subjects(

subject_id INTEGER PRIMARY KEY AUTOINCREMENT,

subject_name TEXT,

credits INTEGER,

semester INTEGER

)

""")


# MARKS TABLE
cursor.execute("""

CREATE TABLE IF NOT EXISTS marks(

mark_id INTEGER PRIMARY KEY AUTOINCREMENT,

student_id INTEGER,

subject_id INTEGER,

marks INTEGER,

grade TEXT,

FOREIGN KEY(student_id)

REFERENCES students(student_id),

FOREIGN KEY(subject_id)

REFERENCES subjects(subject_id)

)

""")

conn.commit()

conn.close()

print("Database Created")