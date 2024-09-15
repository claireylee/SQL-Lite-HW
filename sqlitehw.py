import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

#step 1: set up the database
conn = sqlite3.connect('student_grades.db')
cursor = conn.cursor() #cursor obect to interact with the database

# step 2: create the necessary tables
# student table: id, first name, last name
cursor.execute('''
CREATE TABLE IF NOT EXISTS students (
    student_id INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name TEXT,
    last_name TEXT
)
''')
# grades table: id, student id, subject, grade
cursor.execute('''
CREATE TABLE IF NOT EXISTS grades (
    grade_id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER,
    subject TEXT,
    grade INTEGER,
    FOREIGN KEY (student_id) REFERENCES students(student_id)
)
''')

# insert data into the tables
# at least 5 students
students_data = [
    ('Alice', 'Johnson'),
    ('Bob', 'Smith'),
    ('Carol', 'White'),
    ('David', 'Brown'),
    ('Eve', 'Davis')
]

cursor.executemany('''
INSERT INTO students (first_name, last_name)
VALUES (?, ?)
''', students_data)

# at least 3 grades for each student
grades_data = [
    (1, 'Math', 95),
    (1, 'English', 88),
    (1, 'History', 90),
    (2, 'Math', 82),
    (2, 'English', 76),
    (2, 'History', 85),
    (3, 'Math', 91),
    (3, 'English', 89),
    (3, 'History', 93),
    (4, 'Math', 77),
    (4, 'English', 85),
    (4, 'History', 83),
    (5, 'Math', 89),
    (5, 'English', 92),
    (5, 'History', 87)
]

cursor.executemany('''
INSERT INTO grades (student_id, subject, grade)
VALUES (?, ?, ?)
''', grades_data)

# commit the changes
conn.commit()

# step 4: perform SQL queries

# 1. retrieve all students' names and their grades
cursor.execute('''
SELECT students.first_name, students.last_name, grades.subject, grades.grade
FROM students
JOIN grades ON students.student_id = grades.student_id
''')
students_grades = cursor.fetchall()
print("All students' names and their grades:")
for row in students_grades:
    print(row)

# 2. find the average grade for each student
cursor.execute('''
SELECT students.first_name, students.last_name, AVG(grades.grade) AS avg_grade
FROM students
JOIN grades ON students.student_id = grades.student_id
GROUP BY students.student_id
''')
avg_grades = cursor.fetchall()
print("\nAverage grade for each student:")
for row in avg_grades:
    print(row)

# 3. find the student with the highest average grade
cursor.execute('''
SELECT students.first_name, students.last_name, AVG(grades.grade) AS avg_grade
FROM students
JOIN grades ON students.student_id = grades.student_id
GROUP BY students.student_id
ORDER BY avg_grade DESC
LIMIT 1
''')
top_student = cursor.fetchone()
print(f"\nStudent with the highest average grade: {top_student}")

# 4. find the average grade for the math subject
cursor.execute('''
SELECT AVG(grade) AS avg_math_grade
FROM grades
WHERE subject = 'Math'
''')
avg_math = cursor.fetchone()
print(f"\nAverage grade for Math: {avg_math[0]}")

# 5. list all students who scored above 90 in any subject
cursor.execute('''
SELECT students.first_name, students.last_name, grades.subject, grades.grade
FROM students
JOIN grades ON students.student_id = grades.student_id
WHERE grades.grade > 90
''')
high_scorers = cursor.fetchall()
print("\nStudents who scored above 90 in any subject:")
for row in high_scorers:
    print(row)

# step 5: load data into pandas
df_students = pd.read_sql_query('SELECT * FROM students', conn)
df_grades = pd.read_sql_query('SELECT * FROM grades', conn)

# use join
df_combined = pd.read_sql_query('''
SELECT students.first_name, students.last_name, grades.subject, grades.grade
FROM students
JOIN grades ON students.student_id = grades.student_id
''', conn)

print("\nCombined Data (Pandas DataFrame):")
print(df_combined)

# visualization using matplotlib

# plot the average grades for each student
df_avg_grades = pd.read_sql_query('''
SELECT students.first_name, AVG(grades.grade) AS avg_grade
FROM students
JOIN grades ON students.student_id = grades.student_id
GROUP BY students.student_id
''', conn)

plt.figure(figsize=(8, 6))
plt.plot(df_avg_grades['first_name'], df_avg_grades['avg_grade'], marker='o', linestyle='-', color='b')
plt.xlabel('Student')
plt.ylabel('Average Grade')
plt.title('Average Grades for Each Student')
plt.xticks(rotation=45)
plt.grid(True)
plt.show()

# create a bar chart showing the average grade for each subject
df_avg_subject = pd.read_sql_query('''
SELECT subject, AVG(grade) AS avg_grade
FROM grades
GROUP BY subject
''', conn)

plt.figure(figsize=(3, 5))
plt.bar(df_avg_subject['subject'], df_avg_subject['avg_grade'], color='orange')
plt.xlabel('Subject')
plt.ylabel('Average Grade')
plt.title('Average Grade for Each Subject')
plt.show()


# bonus task: find student with the highest grade in each subject
df_highest_grades = pd.read_sql_query('''
SELECT grades.subject, students.first_name, students.last_name, grades.grade
FROM grades
JOIN students ON grades.student_id = students.student_id
WHERE (grades.subject, grades.grade) IN (
    SELECT subject, MAX(grade)
    FROM grades
    GROUP BY subject
);
''', conn)

# graph and dataframe
print(df_highest_grades)

plt.figure(figsize=(5, 5))
sns.barplot(x='subject', y='grade', hue='first_name', data=df_highest_grades, dodge=True)

plt.xlabel('Subject')
plt.ylabel('Highest Grade')
plt.title('Student with the Highest Grade in Each Subject')
plt.xticks(rotation=45)
plt.legend(title='Student')
plt.grid(True, axis='y')

plt.show()

# close database connection
conn.close()
