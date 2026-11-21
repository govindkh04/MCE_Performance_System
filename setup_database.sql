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

-- 2. Insert All 23 Group Students
INSERT INTO students (roll_no, name, semester, sem1_sgpa, sem2_sgpa, overall_attendance) VALUES
('25/MC/045', 'BIBEK SANJEEV', 3, 8.20, 8.45, 88.00),
('25/MC/046', 'CHETAN', 3, 7.65, 7.90, 81.50),
('25/MC/047', 'DAKSH ARYA', 3, 8.50, 8.70, 90.20),
('25/MC/048', 'DAKSH SHARMA', 3, 6.45, 6.20, 67.50),
('25/MC/049', 'DAKSHITA MALIK', 3, 8.90, 9.10, 93.00),
('25/MC/050', 'DEBRUP MUKHERJEE', 3, 7.80, 8.05, 84.00),
('25/MC/051', 'DEVAANG SINGH', 3, 9.15, 9.35, 95.40),
('25/MC/052', 'DEVANSHI JAISWAL', 3, 7.10, 7.35, 76.20),
('25/MC/053', 'DHEER BHARDWAJ', 3, 8.85, 9.05, 92.80),
('25/MC/054', 'DHEERAJ', 3, 8.40, 8.60, 89.50),
('25/MC/055', 'DHRUV RASTOGI', 3, 9.05, 9.20, 94.10),
('25/MC/056', 'DHRUV VARSHNEY', 3, 7.50, 7.75, 80.00),
('25/MC/057', 'DILIP', 3, 8.15, 8.30, 86.40),
('25/MC/058', 'DILPREET SINGH', 3, 5.85, 6.05, 61.50),
('25/MC/059', 'DINESH KUMAR RAJAK', 3, 7.30, 7.55, 78.90),
('25/MC/060', 'DIVYA JASSAL', 3, 8.00, 8.25, 85.20),
('25/MC/061', 'FAIZA IRFAN', 3, 6.90, 6.75, 71.00),
('25/MC/062', 'GAURAV', 3, 8.60, 8.75, 91.00),
('25/MC/063', 'GOPESH SEHGAL', 3, 7.40, 7.60, 79.50),
('25/MC/064', 'GOVIND KHANDELWAL', 3, 7.95, 8.10, 83.80),
('25/MC/065', 'GREEK KUMAR', 3, 8.30, 8.50, 87.60);


-- 3. Insert Subject-Wise Marks & Attendance (Internal /30, External /70)

INSERT INTO performance
(roll_no, course_code, internal_marks, external_marks, subject_attendance)
VALUES

-- 25/MC/045 - BIBEK SANJEEV
('25/MC/045', 'MC-201', 25, 56, 89.0), ('25/MC/045', 'MC-203', 23, 51, 86.0), ('25/MC/045', 'MC-205', 26, 58, 90.0), ('25/MC/045', 'MC-207', 22, 50, 87.0), ('25/MC/045', 'MC-209', 26, 59, 88.0),

-- 25/MC/046 - CHETAN
('25/MC/046', 'MC-201', 22, 49, 82.0), ('25/MC/046', 'MC-203', 20, 45, 80.0), ('25/MC/046', 'MC-205', 23, 51, 83.0), ('25/MC/046', 'MC-207', 21, 46, 81.0), ('25/MC/046', 'MC-209', 24, 53, 81.5),

-- 25/MC/047 - DAKSH ARYA
('25/MC/047', 'MC-201', 26, 58, 91.0), ('25/MC/047', 'MC-203', 24, 55, 89.0), ('25/MC/047', 'MC-205', 27, 60, 92.0), ('25/MC/047', 'MC-207', 24, 53, 89.0), ('25/MC/047', 'MC-209', 27, 61, 90.0),

-- 25/MC/048 - DAKSH SHARMA
('25/MC/048', 'MC-201', 17, 36, 69.0), ('25/MC/048', 'MC-203', 12, 22, 64.0), ('25/MC/048', 'MC-205', 16, 33, 68.0), ('25/MC/048', 'MC-207', 15, 30, 66.5), ('25/MC/048', 'MC-209', 18, 39, 70.0),

-- 25/MC/049 - DAKSHITA MALIK
('25/MC/049', 'MC-201', 28, 62, 94.0), ('25/MC/049', 'MC-203', 27, 59, 92.0), ('25/MC/049', 'MC-205', 28, 63, 95.0), ('25/MC/049', 'MC-207', 26, 58, 91.0), ('25/MC/049', 'MC-209', 29, 64, 93.0),

-- 25/MC/050 - DEBRUP MUKHERJEE
('25/MC/050', 'MC-201', 23, 51, 85.0), ('25/MC/050', 'MC-203', 21, 47, 82.0), ('25/MC/050', 'MC-205', 24, 52, 85.0), ('25/MC/050', 'MC-207', 22, 48, 83.0), ('25/MC/050', 'MC-209', 25, 54, 85.0),

-- 25/MC/051 - DEVAANG SINGH
('25/MC/051', 'MC-201', 29, 64, 96.0), ('25/MC/051', 'MC-203', 28, 62, 94.0), ('25/MC/051', 'MC-205', 29, 65, 97.0), ('25/MC/051', 'MC-207', 27, 61, 94.0), ('25/MC/051', 'MC-209', 29, 66, 96.0),

-- 25/MC/052 - DEVANSHI JAISWAL
('25/MC/052', 'MC-201', 20, 44, 77.0), ('25/MC/052', 'MC-203', 18, 39, 75.0), ('25/MC/052', 'MC-205', 21, 45, 77.0), ('25/MC/052', 'MC-207', 19, 41, 75.0), ('25/MC/052', 'MC-209', 22, 47, 77.0),

-- 25/MC/053 - DHEER BHARDWAJ
('25/MC/053', 'MC-201', 28, 62, 94.0), ('25/MC/053', 'MC-203', 26, 58, 91.0), ('25/MC/053', 'MC-205', 28, 63, 94.0), ('25/MC/053', 'MC-207', 25, 57, 91.0), ('25/MC/053', 'MC-209', 29, 64, 94.0),

-- 25/MC/054 - DHEERAJ
('25/MC/054', 'MC-201', 25, 57, 90.0), ('25/MC/054', 'MC-203', 24, 53, 88.0), ('25/MC/054', 'MC-205', 26, 58, 91.0), ('25/MC/054', 'MC-207', 23, 52, 88.5), ('25/MC/054', 'MC-209', 26, 60, 90.0),

-- 25/MC/055 - DHRUV RASTOGI
('25/MC/055', 'MC-201', 28, 63, 95.0), ('25/MC/055', 'MC-203', 27, 61, 93.0), ('25/MC/055', 'MC-205', 29, 64, 95.0), ('25/MC/055', 'MC-207', 27, 60, 93.5), ('25/MC/055', 'MC-209', 29, 65, 94.0),

-- 25/MC/056 - DHRUV VARSHNEY
('25/MC/056', 'MC-201', 22, 48, 81.0), ('25/MC/056', 'MC-203', 20, 44, 79.0), ('25/MC/056', 'MC-205', 22, 50, 80.5), ('25/MC/056', 'MC-207', 20, 45, 79.0), ('25/MC/056', 'MC-209', 23, 52, 80.5),

-- 25/MC/057 - DILIP
('25/MC/057', 'MC-201', 24, 54, 87.0), ('25/MC/057', 'MC-203', 22, 50, 85.0), ('25/MC/057', 'MC-205', 25, 56, 87.5), ('25/MC/057', 'MC-207', 22, 49, 85.5), ('25/MC/057', 'MC-209', 26, 57, 87.0),

-- 25/MC/058 - DILPREET SINGH
('25/MC/058', 'MC-201', 14, 28, 63.0), ('25/MC/058', 'MC-203', 10, 19, 59.0), ('25/MC/058', 'MC-205', 13, 24, 61.0), ('25/MC/058', 'MC-207', 11, 21, 60.5), ('25/MC/058', 'MC-209', 15, 30, 64.0),

-- 25/MC/059 - DINESH KUMAR RAJAK
('25/MC/059', 'MC-201', 21, 46, 80.0), ('25/MC/059', 'MC-203', 19, 41, 77.5), ('25/MC/059', 'MC-205', 21, 47, 79.5), ('25/MC/059', 'MC-207', 19, 43, 78.0), ('25/MC/059', 'MC-209', 22, 49, 79.5),

-- 25/MC/060 - DIVYA JASSAL
('25/MC/060', 'MC-201', 24, 53, 86.0), ('25/MC/060', 'MC-203', 22, 49, 84.0), ('25/MC/060', 'MC-205', 24, 55, 86.0), ('25/MC/060', 'MC-207', 21, 48, 84.5), ('25/MC/060', 'MC-209', 25, 56, 85.5),

-- 25/MC/061 - FAIZA IRFAN
('25/MC/061', 'MC-201', 19, 42, 72.0), ('25/MC/061', 'MC-203', 16, 35, 69.5), ('25/MC/061', 'MC-205', 18, 40, 71.5), ('25/MC/061', 'MC-207', 17, 37, 70.0), ('25/MC/061', 'MC-209', 20, 44, 72.0),

-- 25/MC/062 - GAURAV
('25/MC/062', 'MC-201', 26, 59, 92.0), ('25/MC/062', 'MC-203', 25, 55, 90.0), ('25/MC/062', 'MC-205', 27, 60, 92.0), ('25/MC/062', 'MC-207', 24, 54, 89.5), ('25/MC/062', 'MC-209', 27, 62, 91.5),

-- 25/MC/063 - GOPESH SEHGAL
('25/MC/063', 'MC-201', 21, 47, 80.5), ('25/MC/063', 'MC-203', 19, 42, 78.0), ('25/MC/063', 'MC-205', 22, 48, 80.0), ('25/MC/063', 'MC-207', 20, 43, 78.5), ('25/MC/063', 'MC-209', 23, 50, 80.5),

-- 25/MC/064 - GOVIND KHANDELWAL
('25/MC/064', 'MC-201', 23, 52, 84.5), ('25/MC/064', 'MC-203', 21, 48, 82.5), ('25/MC/064', 'MC-205', 24, 53, 84.5), ('25/MC/064', 'MC-207', 22, 49, 83.0), ('25/MC/064', 'MC-209', 25, 55, 84.5),

-- 25/MC/065 - GREEK KUMAR
('25/MC/065', 'MC-201', 25, 56, 88.5), ('25/MC/065', 'MC-203', 23, 52, 86.5), ('25/MC/065', 'MC-205', 26, 57, 88.5), ('25/MC/065', 'MC-207', 23, 51, 86.5), ('25/MC/065', 'MC-209', 26, 58, 88.0);