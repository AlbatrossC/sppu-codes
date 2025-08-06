-- Part A: Design and Develop SQL DDL statements which demonstrate the use of SQL objects such as Table,View, Index, Sequence, Synonym, different constraints etc. 

-- Create the 'office' database
CREATE DATABASE office;

-- Switch to the 'office' database
USE office;

-- Create the 'employees' table with various constraints
CREATE TABLE employees (
    emp_id INT PRIMARY KEY,
    emp_name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE,
    department VARCHAR(50),
    salary DECIMAL(10, 2) CHECK (salary >= 0)
);

-- Insert multiple employee records into the 'employees' table
INSERT INTO employees (emp_id, emp_name, email, department, salary) VALUES
    (101, 'Virat Kohli', 'virat.kohli@gmail.com', 'HR', 45000.00),
    (102, 'Deepika Padukone', 'deepika.padukone@gmail.com', 'IT', 60000.00),
    (103, 'Amitabh Bachchan', 'amitabh.bachchan@gmail.com', 'Finance', 55000.00),
    (104, 'Alia Bhatt', 'alia.bhatt@gmail.com', 'IT', 62000.00),
    (105, 'MS Dhoni', 'ms.dhoni@gmail.com', 'Marketing', 48000.00),
    (106, 'Ratan Tata', 'ratan.tata@gmail.com', 'Finance', 53000.00),
    (107, 'Kangana Ranaut', 'kangana.ranaut@gmail.com', 'HR', 47000.00),
    (108, 'Narayana Murthy', 'narayana.murthy@gmail.com', 'Sales', 51000.00);

-- Display all employees
SELECT * FROM employees;

-- Create a view to show only IT department employees
CREATE VIEW view_it_employees AS
SELECT emp_id, emp_name, salary
FROM employees
WHERE department = 'IT';

-- Display all records from the IT department view
SELECT * FROM view_it_employees;

-- Create an index on the 'department' column
CREATE INDEX idx_department ON employees(department);

-- Use the department index in a query
SELECT * FROM employees WHERE department = 'IT';

-- Create an index on the 'salary' column
CREATE INDEX idx_salary ON employees(salary);

-- Use the salary index in a query
SELECT * FROM employees WHERE salary > 50000;

-- MySQL has no SEQUENCE object, so we use AUTO_INCREMENT for primary key
CREATE TABLE departments (
    dept_id INT AUTO_INCREMENT PRIMARY KEY,
    dept_name VARCHAR(100) NOT NULL UNIQUE
);

-- Insert multiple department names into the 'departments' table
INSERT INTO departments (dept_name) VALUES
    ('HR'),
    ('IT'),
    ('Finance'),
    ('Marketing'),
    ('Sales');

-- Display all departments
SELECT * FROM departments;
