-- Create the database
CREATE DATABASE college;

-- Use the database
USE college;

-- Create 'courses' table
CREATE TABLE courses (
    course_id INT PRIMARY KEY AUTO_INCREMENT,
    course_name VARCHAR(100),
    instructor VARCHAR(100)
);

-- Create 'students' table with a foreign key reference
CREATE TABLE students (
    student_id INT PRIMARY KEY AUTO_INCREMENT,
    student_name VARCHAR(100),
    age INT,
    gender VARCHAR(10),
    course_id INT,
    FOREIGN KEY (course_id) REFERENCES courses(course_id)
);

-- Insert courses
INSERT INTO courses (course_name, instructor) VALUES
('Mathematics', 'Prof. Anderson'),
('Physics', 'Prof. Brown'),
('Chemistry', 'Prof. Carter'),
('Biology', 'Prof. Davis'),
('Computer Science', 'Prof. Evans');

-- Insert students
INSERT INTO students (student_name, age, gender, course_id) VALUES
('John Smith', 20, 'Male', 1),
('Tom Williams', 21, 'Male', 2),
('Duke Johnson', 22, 'Male', 3),
('Alice Brown', 20, 'Female', 4),
('Bob Miller', 23, 'Male', NULL);

-- Query 1: Display all students with their course names using INNER JOIN
SELECT s.student_name, c.course_name, c.instructor
FROM students s
INNER JOIN courses c
ON s.course_id = c.course_id;

-- Query 2: Show all students and their courses using LEFT JOIN
SELECT s.student_name, c.course_name
FROM students s
LEFT JOIN courses c
ON s.course_id = c.course_id;

-- Query 3: Show all courses and the students enrolled using RIGHT JOIN
SELECT s.student_name, c.course_name
FROM students s
RIGHT JOIN courses c
ON s.course_id = c.course_id;

-- Query 4: Find all students enrolled in 'Computer Science' using a SUBQUERY
SELECT student_name
FROM students
WHERE course_id = (
    SELECT course_id FROM courses WHERE course_name = 'Computer Science'
);

-- Query 5: Find all courses that have no students enrolled
SELECT course_name
FROM courses
WHERE course_id NOT IN (SELECT course_id FROM students WHERE course_id IS NOT NULL);

-- Query 6: Create a VIEW to show combined student and course information
CREATE VIEW student_course_view AS
SELECT s.student_id, s.student_name, s.age, s.gender, c.course_name, c.instructor
FROM students s
LEFT JOIN courses c ON s.course_id = c.course_id;

-- Query 7: Select data from the VIEW
SELECT * FROM student_course_view;

-- Query 8: Update a student's course using a SUBQUERY
UPDATE students
SET course_id = (
    SELECT course_id FROM courses WHERE course_name = 'Chemistry'
)
WHERE student_name = 'Bob Miller';

-- Query 9: Delete a student who is not enrolled in any course
DELETE FROM students
WHERE course_id IS NULL;

-- Query 10: Select all courses ordered by instructor name
SELECT course_name, instructor
FROM courses
ORDER BY instructor ASC;