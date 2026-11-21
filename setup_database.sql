CREATE DATABASE IF NOT EXISTS mce_group_performance;
USE mce_group_performance;

DROP TABLE IF EXISTS performance;
DROP TABLE IF EXISTS subjects;
DROP TABLE IF EXISTS students;

CREATE TABLE students (
    roll_no VARCHAR(15) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    semester INT NOT NULL DEFAULT 3,
    sem1_sgpa DECIMAL(4, 2),
    sem2_sgpa DECIMAL(4, 2),
    overall_attendance DECIMAL(5, 2)
);

CREATE TABLE subjects (
    course_code VARCHAR(15) PRIMARY KEY,
    short_name VARCHAR(20) NOT NULL,
    course_name VARCHAR(100) NOT NULL,
    credits INT NOT NULL DEFAULT 4
);

CREATE TABLE performance (
    record_id INT AUTO_INCREMENT PRIMARY KEY,
    roll_no VARCHAR(15),
    course_code VARCHAR(15),
    internal_marks DECIMAL(5, 2),
    external_marks DECIMAL(5, 2),
    subject_attendance DECIMAL(5, 2),
    UNIQUE(roll_no, course_code),
    FOREIGN KEY (roll_no) REFERENCES students(roll_no) ON DELETE CASCADE,
    FOREIGN KEY (course_code) REFERENCES subjects(course_code) ON DELETE CASCADE
);

-- 1. Insert Courses
INSERT INTO subjects VALUES
('MC-201', 'DS', 'Data Structures', 4),
('MC-203', 'RA', 'Real Analysis', 4),
('MC-205', 'PNS', 'Probability and Statistics', 4),
('MC-207', 'MA', 'Modern Algebra', 4),
('MC-209', 'DBMS', 'Database Management Systems', 4);

-- 2. Insert students
INSERT INTO students (roll_no, name, semester, sem1_sgpa, sem2_sgpa, overall_attendance) VALUES
('25/MC/045', 'BIBEK SANJEEV', 3, NULL, NULL, NULL),
('25/MC/046', 'CHETAN', 3, NULL, NULL, NULL),
('25/MC/047', 'DAKSH ARYA', 3, NULL, NULL, NULL),
('25/MC/048', 'DAKSH SHARMA', 3, NULL, NULL, NULL),
('25/MC/049', 'DAKSHITA MALIK', 3, NULL, NULL, NULL),
('25/MC/050', 'DEBRUP MUKHERJEE', 3, NULL, NULL, NULL),
('25/MC/051', 'DEVAANG SINGH', 3, NULL, NULL, NULL),
('25/MC/052', 'DEVANSHI JAISWAL', 3, NULL, NULL, NULL),
('25/MC/053', 'DHEER BHARDWAJ', 3, NULL, NULL, NULL),
('25/MC/054', 'DHEERAJ', 3, NULL, NULL, NULL),
('25/MC/055', 'DHRUV RASTOGI', 3, NULL, NULL, NULL),
('25/MC/056', 'DHRUV VARSHNEY', 3, NULL, NULL, NULL),
('25/MC/057', 'DILIP', 3, NULL, NULL, NULL),
('25/MC/058', 'DILPREET SINGH', 3, NULL, NULL, NULL),
('25/MC/059', 'DINESH KUMAR RAJAK', 3, NULL, NULL, NULL),
('25/MC/060', 'DIVYA JASSAL', 3, NULL, NULL, NULL),
('25/MC/061', 'FAIZA IRFAN', 3, NULL, NULL, NULL),
('25/MC/062', 'GAURAV', 3, NULL, NULL, NULL),
('25/MC/063', 'GOPESH SEHGAL', 3, NULL, NULL, NULL),
('25/MC/064', 'GOVIND KHANDELWAL', 3, NULL, NULL, NULL),
('25/MC/065', 'GREEK KUMAR', 3, NULL, NULL, NULL);