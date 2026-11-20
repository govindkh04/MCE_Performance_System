"""
MCE GROUP PERFORMANCE MANAGEMENT SYSTEM
Works on the database `mce_group_performance` (tables: students, subjects, performance)

BEFORE RUNNING
  1. Open your SQL script in MySQL Workbench and run it once (lightning icon).
  2. pip install mysql-connector-python
  3. Set DB_PASSWORD below (or the DB_PASSWORD environment variable).
  4. python mce_performance_system.py

Login ->  username: admin   password: Admin@123
"""

import os
import csv
import hashlib

import mysql.connector
from mysql.connector import Error

# ------------------------------------------------------------------ CONFIG
DB_HOST = "localhost"
DB_USER = "root"
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_NAME = "mce_group_performance"

ADMIN_USER =  "govind"
ADMIN_HASH = hashlib.sha256("Admin@123".encode()).hexdigest()

PASS_MARK = 40            # minimum total (out of 100) to clear a subject
ATT_SHORTAGE = 75         # attendance below this = shortage
ATT_DETENTION = 65        # attendance below this = detention risk
MAX_INTERNAL, MAX_EXTERNAL = 30, 70

db = None
cu = None


# ------------------------------------------------------------------ HELPERS
def fetch(sql, params=()):
    cu.execute(sql, params)
    return cu.fetchall()


def execute(sql, params=()):
    cu.execute(sql, params)
    db.commit()


def show_table(headers, rows):
    if not rows:
        print("\n  (no records found)\n")
        return
    rows = [[("" if v is None else str(v)) for v in r] for r in rows]
    widths = [max(len(str(h)), *(len(r[i]) for r in rows)) for i, h in enumerate(headers)]
    line = "+" + "+".join("-" * (w + 2) for w in widths) + "+"
    print(line)
    print("| " + " | ".join(str(h).ljust(w) for h, w in zip(headers, widths)) + " |")
    print(line)
    for r in rows:
        print("| " + " | ".join(v.ljust(w) for v, w in zip(r, widths)) + " |")
    print(line)


def ask_int(prompt, lo=None, hi=None):
    while True:
        try:
            v = int(input(prompt))
            if (lo is not None and v < lo) or (hi is not None and v > hi):
                print(f"  Enter a number between {lo} and {hi}.")
                continue
            return v
        except ValueError:
            print("  Please enter a valid number.")


def ask_float(prompt, lo, hi):
    while True:
        try:
            v = float(input(prompt))
            if v < lo or v > hi:
                print(f"  Enter a value between {lo} and {hi}.")
                continue
            return v
        except ValueError:
            print("  Please enter a valid number.")


def f(x):
    """Decimal/None -> float/None."""
    return None if x is None else float(x)


def grade_of(total):
    """Returns (grade, grade point) for a total out of 100."""
    if total >= 90: return "O", 10
    if total >= 80: return "A+", 9
    if total >= 70: return "A", 8
    if total >= 60: return "B+", 7
    if total >= 50: return "B", 6
    if total >= PASS_MARK: return "C", 5
    return "F", 0


def student_exists(roll):
    return bool(fetch("SELECT 1 FROM students WHERE roll_no=%s", (roll,)))


def show_subjects_short():
    show_table(["Code", "Short", "Course", "Credits"],
               fetch("SELECT course_code, short_name, course_name, credits FROM subjects ORDER BY course_code"))


def resolve_course(text):
    """Accept course code (MC-201) or short name (DS); return course_code or None."""
    t = text.strip().upper()
    row = fetch("SELECT course_code FROM subjects WHERE course_code=%s OR short_name=%s", (t, t))
    return row[0][0] if row else None


# ------------------------------------------------------------------ ANALYTICS CORE
def build_summary(rows):
    """
    rows: (roll, name, sem1, sem2, overall_att, credits, internal, external)
    Returns dict roll -> summary with projected sem-3 SGPA, CGPA, backlogs, etc.
    """
    data = {}
    for roll, name, s1, s2, att, cr, i, e in rows:
        d = data.setdefault(roll, {"roll": roll, "name": name, "sem1": f(s1), "sem2": f(s2),
                                   "att": f(att), "pts": 0.0, "credits": 0, "totals": [],
                                   "backlogs": 0})
        if i is None or e is None:
            continue
        total = float(i) + float(e)
        _, gp = grade_of(total)
        d["pts"] += gp * cr
        d["credits"] += cr
        d["totals"].append(total)
        if total < PASS_MARK:
            d["backlogs"] += 1

    for d in data.values():
        d["sem3"] = round(d["pts"] / d["credits"], 2) if d["credits"] else None
        d["avg"] = round(sum(d["totals"]) / len(d["totals"]), 1) if d["totals"] else None
        sgpas = [x for x in (d["sem1"], d["sem2"], d["sem3"]) if x is not None]
        d["cgpa"] = round(sum(sgpas) / len(sgpas), 2) if sgpas else None
    return data


def load_summary():
    rows = fetch("SELECT s.roll_no, s.name, s.sem1_sgpa, s.sem2_sgpa, s.overall_attendance, "
                 "sub.credits, p.internal_marks, p.external_marks "
                 "FROM students s LEFT JOIN performance p ON p.roll_no = s.roll_no "
                 "LEFT JOIN subjects sub ON sub.course_code = p.course_code "
                 "ORDER BY s.roll_no")
    return build_summary(rows)


def ranked(data):
    lst = sorted(data.values(), key=lambda d: (d["cgpa"] is None, -(d["cgpa"] or 0)))
    return [(i + 1, d) for i, d in enumerate(lst)]


def status_of(d):
    flags = []
    if d["backlogs"]:
        flags.append(f"BACKLOG x{d['backlogs']}")
    if d["att"] is not None:
        if d["att"] < ATT_DETENTION:
            flags.append("DETENTION RISK")
        elif d["att"] < ATT_SHORTAGE:
            flags.append("ATT. SHORTAGE")
    return ", ".join(flags) if flags else "OK"


# ------------------------------------------------------------------ 1. STUDENTS
def students_menu():
    cols = ["Roll No", "Name", "Sem", "Sem1 SGPA", "Sem2 SGPA", "Attendance %"]
    base = "SELECT roll_no, name, semester, sem1_sgpa, sem2_sgpa, overall_attendance FROM students"
    editable = {"1": ("semester", "Semester"), "2": ("sem1_sgpa", "Sem-1 SGPA"),
                "3": ("sem2_sgpa", "Sem-2 SGPA"), "4": ("overall_attendance", "Overall attendance %")}
    while True:
        print("\n--- STUDENTS ---")
        print("1. View all\n2. Search by roll no.\n3. Search by name\n4. Add student\n"
              "5. Update a student detail\n6. Delete student\n7. Back")
        ch = ask_int("Enter choice :- ", 1, 7)
        if ch == 1:
            show_table(cols, fetch(base + " ORDER BY roll_no"))
        elif ch == 2:
            r = input("Roll no (e.g. 25/MC/030) :- ").strip().upper()
            show_table(cols, fetch(base + " WHERE roll_no=%s", (r,)))
        elif ch == 3:
            n = input("Name (or part of it) :- ").strip()
            show_table(cols, fetch(base + " WHERE name LIKE %s ORDER BY roll_no", (f"%{n}%",)))
        elif ch == 4:
            r = input("Roll no :- ").strip().upper()
            n = input("Name :- ").strip().upper()
            s1 = ask_float("Sem-1 SGPA (0-10) :- ", 0, 10)
            s2 = ask_float("Sem-2 SGPA (0-10) :- ", 0, 10)
            att = ask_float("Overall attendance % :- ", 0, 100)
            try:
                execute("INSERT INTO students (roll_no, name, semester, sem1_sgpa, sem2_sgpa, "
                        "overall_attendance) VALUES (%s,%s,3,%s,%s,%s)", (r, n, s1, s2, att))
                print("Student added.")
            except Error as e:
                print("Could not add:", e.msg)
        elif ch == 5:
            r = input("Roll no :- ").strip().upper()
            if not student_exists(r):
                print("No such student.")
                continue
            for k, (_, label) in editable.items():
                print(f"{k}. {label}")
            k = input("Which detail? :- ").strip()
            if k not in editable:
                print("Invalid choice.")
                continue
            col, label = editable[k]
            val = ask_int(f"New {label} :- ", 1, 8) if k == "1" else \
                ask_float(f"New {label} :- ", 0, 10 if "SGPA" in label else 100)
            execute(f"UPDATE students SET {col}=%s WHERE roll_no=%s", (val, r))   # col is whitelisted
            print("Updated.")
        elif ch == 6:
            r = input("Roll no to delete :- ").strip().upper()
            if input("This also deletes their marks. Sure? (y/n) :- ").lower() == "y":
                execute("DELETE FROM students WHERE roll_no=%s", (r,))
                print("Done.")
        else:
            break


# ------------------------------------------------------------------ 2. SUBJECTS
def subjects_menu():
    while True:
        print("\n--- SUBJECTS ---")
        print("1. View subjects\n2. Add subject\n3. Update subject credits\n"
              "4. Delete subject\n5. Back")
        ch = ask_int("Enter choice :- ", 1, 5)
        if ch == 1:
            show_table(["Code", "Short", "Course", "Credits", "Students", "Class Avg"],
                       fetch("SELECT s.course_code, s.short_name, s.course_name, s.credits, "
                             "COUNT(p.record_id), "
                             "ROUND(AVG(p.internal_marks + p.external_marks), 1) "
                             "FROM subjects s LEFT JOIN performance p ON p.course_code = s.course_code "
                             "GROUP BY s.course_code, s.short_name, s.course_name, s.credits "
                             "ORDER BY s.course_code"))
        elif ch == 2:
            code = input("Course code (e.g. MC-211) :- ").strip().upper()
            short = input("Short name :- ").strip().upper()
            name = input("Course name :- ").strip()
            cr = ask_int("Credits :- ", 1, 8)
            try:
                execute("INSERT INTO subjects VALUES (%s,%s,%s,%s)", (code, short, name, cr))
                print("Subject added.")
            except Error as e:
                print("Could not add:", e.msg)
        elif ch == 3:
            show_subjects_short()
            code = resolve_course(input("Course code or short name :- "))
            if not code:
                print("No such subject.")
                continue
            execute("UPDATE subjects SET credits=%s WHERE course_code=%s",
                    (ask_int("New credits :- ", 1, 8), code))
            print("Updated.")
        elif ch == 4:
            code = resolve_course(input("Course code or short name to delete :- "))
            if code and input("This also deletes its marks. Sure? (y/n) :- ").lower() == "y":
                execute("DELETE FROM subjects WHERE course_code=%s", (code,))
                print("Done.")
        else:
            break


# ------------------------------------------------------------------ 3. MARKS & ATTENDANCE
def report_card(roll):
    srow = fetch("SELECT name, semester, sem1_sgpa, sem2_sgpa, overall_attendance "
                 "FROM students WHERE roll_no=%s", (roll,))
    if not srow:
        print("No such student.")
        return
    name, sem, s1, s2, att = srow[0]
    rows = fetch("SELECT sub.short_name, sub.course_name, sub.credits, p.internal_marks, "
                 "p.external_marks, p.subject_attendance FROM performance p "
                 "JOIN subjects sub ON sub.course_code = p.course_code "
                 "WHERE p.roll_no=%s ORDER BY sub.course_code", (roll,))
    print(f"\n  REPORT CARD  |  {roll}  |  {name}  |  Semester {sem}")
    table = []
    for short, cname, cr, i, e, sa in rows:
        total = float(i) + float(e)
        g, _ = grade_of(total)
        table.append((short, cname, cr, f(i), f(e), total, g,
                      "PASS" if total >= PASS_MARK else "FAIL", f(sa)))
    show_table(["Sub", "Course", "Cr", "Int/30", "Ext/70", "Total", "Grade", "Result", "Att %"], table)

    summ = load_summary().get(roll)
    if summ:
        print(f"  Sem-1 SGPA: {summ['sem1']}   Sem-2 SGPA: {summ['sem2']}   "
              f"Projected Sem-3 SGPA: {summ['sem3']}")
        print(f"  CGPA (avg of 3 sems): {summ['cgpa']}   Average marks: {summ['avg']}")
        print(f"  Overall attendance: {summ['att']}%   Status: {status_of(summ)}")
        pos = {d['roll']: r for r, d in ranked(load_summary())}
        print(f"  Class rank (by CGPA): {pos.get(roll)} / {len(pos)}\n")


def marks_menu():
    while True:
        print("\n--- MARKS & ATTENDANCE ---")
        print("1. Student report card\n2. Enter / update marks\n3. Update subject attendance\n"
              "4. Subject marklist\n5. Subject statistics\n6. Delete a marks record\n7. Back")
        ch = ask_int("Enter choice :- ", 1, 7)
        if ch == 1:
            report_card(input("Roll no :- ").strip().upper())
        elif ch == 2:
            r = input("Roll no :- ").strip().upper()
            if not student_exists(r):
                print("No such student.")
                continue
            show_subjects_short()
            c = resolve_course(input("Course code or short name :- "))
            if not c:
                print("No such subject.")
                continue
            i = ask_float(f"Internal marks (0-{MAX_INTERNAL}) :- ", 0, MAX_INTERNAL)
            e = ask_float(f"External marks (0-{MAX_EXTERNAL}) :- ", 0, MAX_EXTERNAL)
            a = ask_float("Subject attendance % :- ", 0, 100)
            execute("INSERT INTO performance (roll_no, course_code, internal_marks, external_marks, "
                    "subject_attendance) VALUES (%s,%s,%s,%s,%s) ON DUPLICATE KEY UPDATE "
                    "internal_marks=VALUES(internal_marks), external_marks=VALUES(external_marks), "
                    "subject_attendance=VALUES(subject_attendance)", (r, c, i, e, a))
            print("Record saved. Total =", i + e, "| Grade =", grade_of(i + e)[0])
        elif ch == 3:
            r = input("Roll no :- ").strip().upper()
            c = resolve_course(input("Course code or short name :- "))
            if not c:
                print("No such subject.")
                continue
            a = ask_float("New subject attendance % :- ", 0, 100)
            execute("UPDATE performance SET subject_attendance=%s WHERE roll_no=%s AND course_code=%s",
                    (a, r, c))
            print("Updated (if the record existed).")
        elif ch == 4:
            show_subjects_short()
            c = resolve_course(input("Course code or short name :- "))
            if not c:
                print("No such subject.")
                continue
            rows = fetch("SELECT s.roll_no, s.name, p.internal_marks, p.external_marks, "
                         "p.internal_marks + p.external_marks AS total, p.subject_attendance "
                         "FROM performance p JOIN students s ON s.roll_no = p.roll_no "
                         "WHERE p.course_code=%s ORDER BY total DESC, s.roll_no", (c,))
            show_table(["Rank", "Roll No", "Name", "Int", "Ext", "Total", "Grade", "Att %"],
                       [(n + 1, r[0], r[1], f(r[2]), f(r[3]), f(r[4]), grade_of(float(r[4]))[0], f(r[5]))
                        for n, r in enumerate(rows)])
        elif ch == 5:
            show_table(["Subject", "Students", "Average", "Highest", "Lowest", "Pass %", "Failed"],
                       fetch("SELECT sub.short_name, COUNT(*), "
                             "ROUND(AVG(p.internal_marks + p.external_marks), 1), "
                             "MAX(p.internal_marks + p.external_marks), "
                             "MIN(p.internal_marks + p.external_marks), "
                             "ROUND(100 * SUM(p.internal_marks + p.external_marks >= %s) / COUNT(*), 1), "
                             "SUM(p.internal_marks + p.external_marks < %s) "
                             "FROM performance p JOIN subjects sub ON sub.course_code = p.course_code "
                             "GROUP BY sub.course_code, sub.short_name ORDER BY sub.course_code",
                             (PASS_MARK, PASS_MARK)))
        elif ch == 6:
            r = input("Roll no :- ").strip().upper()
            c = resolve_course(input("Course code or short name :- "))
            if c and input("Delete this record? (y/n) :- ").lower() == "y":
                execute("DELETE FROM performance WHERE roll_no=%s AND course_code=%s", (r, c))
                print("Done.")
        else:
            break


# ------------------------------------------------------------------ 4. ANALYTICS
def analytics_menu():
    while True:
        print("\n--- ANALYTICS ---")
        print("1. Class dashboard\n2. Class ranking (by CGPA)\n3. Top 5 performers\n"
              "4. Attendance shortage list\n5. Backlog list (subject-wise)\n"
              "6. At-risk students\n7. SGPA trend (Sem1 -> Sem2 -> projected Sem3)\n"
              "8. Grade distribution per subject\n9. Export summary to CSV\n10. Back")
        ch = ask_int("Enter choice :- ", 1, 10)
        if ch == 10:
            break
        data = load_summary()
        rk = ranked(data)
        if ch == 1:
            n = len(data)
            cg = [d["cgpa"] for d in data.values() if d["cgpa"] is not None]
            at = [d["att"] for d in data.values() if d["att"] is not None]
            clear = sum(1 for d in data.values() if d["backlogs"] == 0)
            print("\n========== CLASS DASHBOARD ==========")
            print(f"  Total students          : {n}")
            print(f"  Average CGPA            : {round(sum(cg) / len(cg), 2) if cg else '-'}")
            print(f"  Average attendance      : {round(sum(at) / len(at), 1) if at else '-'}%")
            print(f"  Students with no backlog: {clear} ({round(100 * clear / n, 1) if n else 0}%)")
            print(f"  Students with backlog   : {n - clear}")
            print(f"  Attendance shortage     : {sum(1 for d in data.values() if d['att'] is not None and d['att'] < ATT_SHORTAGE)}")
            print(f"  Detention risk (<{ATT_DETENTION}%)  : {sum(1 for d in data.values() if d['att'] is not None and d['att'] < ATT_DETENTION)}")
            if rk:
                print(f"  Class topper            : {rk[0][1]['name']} (CGPA {rk[0][1]['cgpa']})")
        elif ch == 2:
            show_table(["Rank", "Roll No", "Name", "Sem1", "Sem2", "Sem3(P)", "CGPA", "Att %", "Status"],
                       [(r, d["roll"], d["name"], d["sem1"], d["sem2"], d["sem3"], d["cgpa"],
                         d["att"], status_of(d)) for r, d in rk])
        elif ch == 3:
            show_table(["Rank", "Roll No", "Name", "CGPA", "Avg Marks", "Att %"],
                       [(r, d["roll"], d["name"], d["cgpa"], d["avg"], d["att"]) for r, d in rk[:5]])
        elif ch == 4:
            low = sorted((d for d in data.values() if d["att"] is not None and d["att"] < ATT_SHORTAGE),
                         key=lambda d: d["att"])
            show_table(["Roll No", "Name", "Attendance %", "Category"],
                       [(d["roll"], d["name"], d["att"],
                         "DETENTION RISK" if d["att"] < ATT_DETENTION else "SHORTAGE") for d in low])
        elif ch == 5:
            show_table(["Roll No", "Name", "Subject", "Internal", "External", "Total"],
                       fetch("SELECT s.roll_no, s.name, sub.course_name, p.internal_marks, "
                             "p.external_marks, p.internal_marks + p.external_marks AS total "
                             "FROM performance p JOIN students s ON s.roll_no = p.roll_no "
                             "JOIN subjects sub ON sub.course_code = p.course_code "
                             "WHERE p.internal_marks + p.external_marks < %s "
                             "ORDER BY s.roll_no, sub.course_code", (PASS_MARK,)))
        elif ch == 6:
            risk = [d for d in data.values() if status_of(d) != "OK"]
            risk.sort(key=lambda d: (-d["backlogs"], d["att"] if d["att"] is not None else 0))
            show_table(["Roll No", "Name", "Backlogs", "Att %", "CGPA", "Flags"],
                       [(d["roll"], d["name"], d["backlogs"], d["att"], d["cgpa"], status_of(d))
                        for d in risk])
        elif ch == 7:
            rows = []
            for d in data.values():
                if d["sem2"] is None or d["sem3"] is None:
                    continue
                diff = round(d["sem3"] - d["sem2"], 2)
                trend = "Improving" if diff >= 0.2 else "Declining" if diff <= -0.2 else "Stable"
                rows.append((d["roll"], d["name"], d["sem1"], d["sem2"], d["sem3"], diff, trend))
            show_table(["Roll No", "Name", "Sem1", "Sem2", "Sem3(P)", "Change", "Trend"], rows)
        elif ch == 8:
            rows = fetch("SELECT sub.short_name, p.internal_marks + p.external_marks "
                         "FROM performance p JOIN subjects sub ON sub.course_code = p.course_code")
            dist = {}
            for short, total in rows:
                g = grade_of(float(total))[0]
                dist.setdefault(short, {k: 0 for k in ["O", "A+", "A", "B+", "B", "C", "F"]})[g] += 1
            show_table(["Subject", "O", "A+", "A", "B+", "B", "C", "F"],
                       [(s,) + tuple(v.values()) for s, v in dist.items()])
        elif ch == 9:
            fname = "mce_performance_summary.csv"
            with open(fname, "w", newline="", encoding="utf-8") as fh:
                w = csv.writer(fh)
                w.writerow(["Rank", "Roll No", "Name", "Sem1", "Sem2", "Sem3(Projected)", "CGPA",
                            "Avg Marks", "Attendance %", "Backlogs", "Status"])
                for r, d in rk:
                    w.writerow([r, d["roll"], d["name"], d["sem1"], d["sem2"], d["sem3"],
                                d["cgpa"], d["avg"], d["att"], d["backlogs"], status_of(d)])
            print(f"Exported to {os.path.abspath(fname)}")


# ------------------------------------------------------------------ MAIN
def login():
    for attempt in range(3):
        u = input("Username :- ").strip()
        p = input("Password :- ")
        if u == ADMIN_USER and hashlib.sha256(p.encode()).hexdigest() == ADMIN_HASH:
            print("Login successful. Welcome, Admin!")
            return True
        print(f"Incorrect credentials ({2 - attempt} attempt(s) left).")
    return False


def connect():
    global db, cu
    try:
        db = mysql.connector.connect(host=DB_HOST, user=DB_USER, password=DB_PASSWORD, database=DB_NAME)
        cu = db.cursor()
        return True
    except Error as e:
        if e.errno == 1049:
            print(f"Database '{DB_NAME}' not found.")
            print("Run your SQL script in MySQL Workbench first, then start this program again.")
        elif e.errno == 1045:
            print("Wrong MySQL username/password. Set DB_PASSWORD at the top of this file.")
        else:
            print("Could not connect to MySQL:", e.msg)
        return False


def main():
    if not connect():
        return
    print("=" * 52)
    print("   MCE GROUP PERFORMANCE MANAGEMENT SYSTEM")
    print("=" * 52)
    if not login():
        print("Too many failed attempts. Exiting.")
        return

    while True:
        print("\n========== MAIN MENU ==========")
        print("1. Students\n2. Subjects\n3. Marks & Attendance\n4. Analytics & Reports\n5. Exit")
        ch = ask_int("Enter choice :- ", 1, 5)
        if ch == 1:
            students_menu()
        elif ch == 2:
            subjects_menu()
        elif ch == 3:
            marks_menu()
        elif ch == 4:
            analytics_menu()
        else:
            print("Goodbye!")
            break

    cu.close()
    db.close()


if __name__ == "__main__":
    main()