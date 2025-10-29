-- Create database and use it
CREATE DATABASE college_db;
USE college_db;

-- Create table
CREATE TABLE students(
    student_id INT PRIMARY KEY,
    student_name VARCHAR(50),
    course VARCHAR(50),
    marks INT
);

-- Insert sample records
INSERT INTO students VALUES
(1, 'Amit Sharma', 'Computer Science', 85),
(2, 'Sneha Patil', 'Information Technology', 78),
(3, 'Rohan Desai', 'Electronics', 90),
(4, 'Neha Joshi', 'Mechanical', 72);

-- Export data to CSV file
SELECT * 
INTO OUTFILE 'C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/students.csv'
FIELDS TERMINATED BY ',' 
LINES TERMINATED BY '\n'
FROM students;

-- Export data to TXT file
SELECT * 
INTO OUTFILE 'C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/students.txt'
FIELDS TERMINATED BY '\t'
LINES TERMINATED BY '\n'
FROM students;

-- Delete all records
DELETE FROM students;

-- Import data from CSV file
LOAD DATA INFILE 'C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/students.csv'
INTO TABLE students
FIELDS TERMINATED BY ',' 
LINES TERMINATED BY '\n'
IGNORE 1 ROWS;

-- Delete all records again
DELETE FROM students;

-- Import data from TXT file
LOAD DATA INFILE 'C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/students.txt'
INTO TABLE students
FIELDS TERMINATED BY '\t'
LINES TERMINATED BY '\n';

-- View all records
SELECT * FROM students;