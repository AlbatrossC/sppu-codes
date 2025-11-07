-- 4a) PL/SQL Question Implementation in MySQL

-- 1. Create database and select it
CREATE DATABASE library_system;
USE library_system;

-- 2. Create tables
CREATE TABLE borrower (
    roll_no INT PRIMARY KEY,
    name VARCHAR(100),
    date_of_issue DATE,
    name_of_book VARCHAR(100),
    status CHAR(1)
);

CREATE TABLE fine (
    roll_no INT,
    date DATE,
    amt INT
);

-- 3. Insert sample data
INSERT INTO borrower VALUES
(1, 'Arun',   '2025-09-13', 'Maths', 'I'),
(2, 'Bina',   '2025-09-11', 'Physics', 'I'),
(3, 'Chetan', '2025-09-10', 'Biology', 'I'),
(4, 'Deepa',  '2025-09-09', 'Chemistry', 'I'),
(5, 'Esha',   '2025-08-10', 'DBMS', 'I'),
(6, 'Farhan', '2025-09-07', 'AI', 'I');

-- 4. View borrower data
SELECT * FROM borrower;

-- 5. Create stored procedure
DELIMITER //
CREATE PROCEDURE fine_check(IN p_roll_no INT, IN p_book VARCHAR(100))
BEGIN
    DECLARE v_days, v_fine INT DEFAULT 0;
    
    SELECT DATEDIFF(CURDATE(), date_of_issue) INTO v_days
    FROM borrower
    WHERE roll_no = p_roll_no AND name_of_book = p_book;
    
    IF v_days > 30 THEN SET v_fine = v_days * 50;
    ELSEIF v_days >= 15 THEN SET v_fine = v_days * 5;
    END IF;
    
    UPDATE borrower SET status = 'R'
    WHERE roll_no = p_roll_no AND name_of_book = p_book;
    
    IF v_fine > 0 THEN
        INSERT INTO fine VALUES (p_roll_no, CURDATE(), v_fine);
    END IF;
END //
DELIMITER ;

-- 6. Execute the procedure
CALL fine_check(6, 'AI');

-- 7. View results
SELECT * FROM fine;