# MCE Group Performance Management System

A command-line application for managing student records, subjects, marks, attendance, and class performance analytics. It uses Python and MySQL, with sample data for 23 students and five courses.

## Features

- Add, search, update, and delete student records
- Add and manage subjects and course credits
- Enter marks and attendance, and generate student report cards
- View subject marklists and statistics
- Review class rankings, top performers, attendance warnings, backlogs, and students at risk
- Export a class performance summary to CSV

## Requirements

- Python 3.8 or later
- MySQL Server
- MySQL Workbench (or another MySQL client) to initialize the database
- `mysql-connector-python`

## Setup

1. Create the database and load the sample data by running [`setup_database.sql`](setup_database.sql) in MySQL Workbench.

   **Note:** The script drops and recreates the `students`, `subjects`, and `performance` tables. Running it again replaces their contents with the included sample data.

2. Install the Python dependency:

   ```bash
   python -m pip install mysql-connector-python
   ```

3. Configure the MySQL password. The application connects to `localhost` as `root` and uses the `mce_group_performance` database. Set `DB_PASSWORD` in your environment before starting the program.

   PowerShell:

   ```powershell
   $env:DB_PASSWORD = "your_mysql_password"
   ```

   macOS/Linux:

   ```bash
   export DB_PASSWORD="your_mysql_password"
   ```

   If your MySQL host, username, or database differs, update `DB_HOST`, `DB_USER`, or `DB_NAME` in `mce_performance_system.py`.

4. Start the application from the project directory:

   ```bash
   python mce_performance_system.py
   ```

## Login

The current credentials configured in the application are:

| Username | Password |
| --- | --- |
| `govind` | `Admin@123` |

The program allows three login attempts per run.

## Using the application

After login, choose a section from the main menu:

1. **Students** — view, search, add, update, or delete student records.
2. **Subjects** — view subjects, add courses, change credits, or delete courses.
3. **Marks & Attendance** — maintain marks and attendance, view report cards, marklists, and subject statistics.
4. **Analytics & Reports** — view the class dashboard, rankings, top five, attendance shortage and backlog lists, at-risk students, SGPA trends, grade distributions, or export a CSV summary.
5. **Exit** — close the program.

The analytics CSV is written to the current working directory as `mce_performance_summary.csv`.

## Database overview

The setup script creates three related tables:

- `students` — student identity, semester, prior SGPAs, and overall attendance
- `subjects` — course code, short name, course name, and credits
- `performance` — student/course marks and subject attendance, with one record per student and course

Deleting a student or subject cascades to their related performance records.

## Grading and status rules

- Marks are recorded as internal out of 30 and external out of 70.
- A total of 40/100 is the pass mark.
- Grade points: O (90+): 10; A+ (80–89): 9; A (70–79): 8; B+ (60–69): 7; B (50–59): 6; C (40–49): 5; F (below 40): 0.
- Attendance below 75% is flagged as a shortage; below 65% is flagged as detention risk.
- Sem-3 SGPA is projected from recorded course grades weighted by course credits. CGPA is the average of available Sem-1, Sem-2, and projected Sem-3 SGPAs.

## Project files

```text
MCE_Performance_System/
├── mce_performance_system.py   # CLI application
├── setup_database.sql          # Schema and sample data
└── README.md                   # Project guide
```
