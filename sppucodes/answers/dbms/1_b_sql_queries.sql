-- Part B:Write at least 10 SQL queries on the suitable database application using SQL DML statements. Note: Instructor will design the queries which demonstrate the use of concepts like Insert, Select, Update, Delete with operators, functions, and set operator etc.

-- Create the database
CREATE DATABASE college;

-- Use the database
USE college;

-- Create Table Students
CREATE TABLE students (
    student_id INT PRIMARY KEY AUTO_INCREMENT,
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    age INT,
    gender VARCHAR(10)
);

-- Create 'courses' table
CREATE TABLE courses (
    course_id INT PRIMARY KEY AUTO_INCREMENT,
    course_name VARCHAR(100),
    instructor VARCHAR(100)
);

-- Insert students
INSERT INTO students (first_name, last_name, age, gender) VALUES
('Aarav', 'Sharma', 20, 'Male'),
('Anaya', 'Verma', 21, 'Female'),
('Vihaan', 'Patel', 22, 'Male'),
('Ishita', 'Mehta', 20, 'Female'),
('Rohan', 'Desai', 23, 'Male');

-- Insert courses
INSERT INTO courses (course_name, instructor) VALUES
('Mathematics', 'Dr. Meena Iyer'),
('Physics', 'Dr. Rajeev Menon'),
('Chemistry', 'Dr. Neha Kulkarni'),
('Biology', 'Dr. Arvind Rao'),
('Computer Science', 'Dr. Priya Nair');

-- Query 1: Select all students whose first name starts with 'A'
SELECT * FROM students
WHERE first_name LIKE 'A%';

-- Query 2: Update the instructor of 'Biology' course
UPDATE courses
SET instructor = 'Dr. Suman Rao'
WHERE course_name = 'Biology';

-- Query 3: Delete a course named 'Physics'
DELETE FROM courses
WHERE course_name = 'Physics';

-- Query 4: Count how many students are male and female
SELECT gender, COUNT(*) AS total_students
FROM students
GROUP BY gender;

-- Query 5: Get the average age of all students
SELECT AVG(age) AS average_age
FROM students;

-- Query 6: Select all students whose age is greater than or equal to 21
SELECT * FROM students
WHERE age >= 21;

-- Query 7: Join students and courses (cross join for demonstration)
SELECT s.first_name, s.last_name, c.course_name
FROM students s
CROSS JOIN courses c;

-- Query 8: Use UNION to combine first names from students and instructors from courses
SELECT first_name AS name FROM students
UNION
SELECT instructor AS name FROM courses;

-- Query 9: Count the number of students grouped by their age
SELECT age, COUNT(*) AS number_of_students
FROM students
GROUP BY age;

-- Query 10: Select all courses ordered by instructor name in ascending order
SELECT course_name, instructor
FROM courses
ORDER BY instructor ASC;