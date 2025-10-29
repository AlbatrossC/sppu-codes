-- Create database and use it
CREATE DATABASE college_db;
USE college_db;

-- Create main (old) roll call table
CREATE TABLE O_Roll_Call (
    roll_no INT PRIMARY KEY,
    student_name VARCHAR(50)
);

-- Create new roll call table
CREATE TABLE N_Roll_Call (
    roll_no INT,
    student_name VARCHAR(50)
);

-- Insert sample data
INSERT INTO O_Roll_Call VALUES
(1, 'Ajay'),
(2, 'Sneha'),
(3, 'Rohan');

INSERT INTO N_Roll_Call VALUES
(2, 'Sneha'), -- duplicate
(3, 'Rohan'), -- duplicate
(4, 'Neha'),  -- new
(5, 'Raj');   -- new

-- STORED PROCEDURE: Parameterized Cursor
DELIMITER //

CREATE PROCEDURE merge_roll_call(IN limit_roll INT)
BEGIN
    DECLARE done INT DEFAULT 0;
    DECLARE r_no INT;
    DECLARE r_name VARCHAR(50);

    -- Declare parameterized cursor
    DECLARE cur CURSOR FOR 
        SELECT roll_no, student_name 
        FROM N_Roll_Call 
        WHERE roll_no <= limit_roll;

    DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = 1;

    OPEN cur;

    read_loop: LOOP
        FETCH cur INTO r_no, r_name;
        IF done THEN
            LEAVE read_loop;
        END IF;

        -- Insert only if not already present
        IF NOT EXISTS (SELECT 1 FROM O_Roll_Call WHERE roll_no = r_no) THEN
            INSERT INTO O_Roll_Call VALUES (r_no, r_name);
        END IF;
    END LOOP;

    CLOSE cur;
END //

DELIMITER ;

-- See initial data
SELECT * FROM O_Roll_Call;
SELECT * FROM N_Roll_Call;

-- Process roll numbers <= 4 (adds Neha)
CALL merge_roll_call(4);
SELECT * FROM O_Roll_Call;

-- Process roll numbers <= 5 (adds Raj)
CALL merge_roll_call(5);
SELECT * FROM O_Roll_Call;

SELECT * FROM O_Roll_Call;
