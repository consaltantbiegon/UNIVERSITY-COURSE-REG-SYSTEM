"""
Title: University Course Registration System – Metrics-Based Refactoring

Project Description:

The following Python code implements a University Course Registration System, but the design has several issues that violate good software engineering principles.

Your task is to:

Analyze the code using software metrics (e.g., CK metrics, Cyclomatic Complexity, LOC, cohesion, coupling).

Identify problematic areas based on metric results.

Refactor the code to improve its maintainability and design quality.


Part A: Metric Analysis (8 Marks)

Calculate the following metrics using manual computation or a tool (e.g., radon, pylint, lizard):

Cyclomatic Complexity (CC) for each method

Lines of Code (LOC)

Coupling Between Objects (CBO)

Depth of Inheritance Tree (DIT)

Lack of Cohesion of Methods (LCOM)

Identify problem areas using metric values (e.g., methods with high CC, classes with low cohesion, high coupling, or long methods).

Part B: Diagnosis (6 Marks)

Explain why these metrics indicate potential design or maintenance problems.

Discuss how high coupling and low cohesion affect reusability, testability etc.

Part C: Refactoring (6 Marks)

Refactor the code to:

Reduce Cyclomatic Complexity in long methods (e.g., calculate_performance, full_report, main).

Reduce coupling between Registrar, Student, and Course.

Improve cohesion and encapsulation.

Provide your refactored code snippets and explain the improvement using before-and-after metrics.

Sumission Requirements:
All instructions are provided in University_Course_Registration_System.py.

Ensure that you include the list of group members and the GitHub link as the first items in your PDF file during submission.
Only one PDF file should be submitted — the code in the GitHub link must also be included in the PDF file.

Organize your work in an easy-to-read format. 
"""

from datetime import datetime
from typing import List, Optional, Dict, Tuple

class Person:
    def __init__(self, person_id: str, name: str, email: str, phone: Optional[str] = None):
        self.person_id = person_id
        self.name = name
        self.email = email
        self.phone = phone
        self.role = None

    def display_info(self) -> None:
        print(f"ID: {self.person_id}, Name: {self.name}, Email: {self.email}, Phone: {self.phone}")

    def update_contact(self, email: str, phone: Optional[str]) -> None:
        self.email = email
        self.phone = phone
        print(f"{self.name}'s contact updated.")

class Student(Person):
    def __init__(self, student_id: str, name: str, email: str, phone: Optional[str] = None):
        super().__init__(student_id, name, email, phone)
        self.role = "Student"
        self.courses: List['Course'] = []
        self.grades: Dict[str, str] = {}           # course_code -> grade (A-F)
        self.attendance: Dict[str, List[bool]] = {} # course_code -> list of attendance booleans
        self.last_login = datetime.now()

    def register_course(self, course: 'Course') -> bool:
        """
        Add course to student's course list if not present.
        Returns True if added, False if already present.
        Note: This method does not modify course.students to avoid cyclic side effects;
        use Course.enroll_student(course, student) or Registrar.enroll(...) for a full enrollment.
        """
        if course.code in {c.code for c in self.courses}:
            return False
        self.courses.append(course)
        return True

    def compute_gpa(self) -> float:
        """
        Compute a credit-weighted GPA using student's recorded grades.
        Uses course credit hours when the course object is available in self.courses,
        otherwise treats the course as 1 credit.
        Returns 0.0 if no grades recorded.
        """
        if not self.grades:
            return 0.0
        points_map = {"A": 4.0, "B": 3.0, "C": 2.0, "D": 1.0, "E": 0.0, "F": 0.0}
        total_weighted_points = 0.0
        total_credits = 0.0
        # Find credit hours by course code where possible
        code_to_course = {c.code: c for c in self.courses}
        for code, grade in self.grades.items():
            pts = points_map.get(grade.upper(), 0.0)
            credit = float(code_to_course.get(code, None).credit_hours) if code in code_to_course else 1.0
            total_weighted_points += pts * credit
            total_credits += credit
        if total_credits == 0:
            return 0.0
        return round(total_weighted_points / total_credits, 2)

    def average_attendance(self) -> float:
        """
        Returns average attendance percent across courses for which attendance exists.
        """
        if not self.attendance:
            return 0.0
        total_pct = 0.0
        count = 0
        for records in self.attendance.values():
            if not records:
                continue
            attended = sum(1 for r in records if r)
            pct = (attended / len(records)) * 100
            total_pct += pct
            count += 1
        return round(total_pct / count, 1) if count else 0.0

    def report_performance(self) -> Tuple[float, float]:
        """
        Prints and returns (gpa, avg_attendance). Uses compute_gpa and average_attendance.
        """
        gpa = self.compute_gpa()
        avg_att = self.average_attendance()
        print(f"{self.name} -> GPA: {gpa}, Attendance: {avg_att:.1f}%")
        if gpa >= 3.5 and avg_att >= 90:
            print("Excellent performance!")
        elif gpa < 2.0 or avg_att < 60:
            print("Warning: Poor performance")
        return gpa, avg_att


class Course:
    def __init__(self, code: str, title: str, credit_hours: int, lecturer: Optional['Lecturer'] = None):
        if credit_hours <= 0:
            raise ValueError("credit_hours must be positive")
        self.code = code
        self.title = title
        self.credit_hours = credit_hours
        self.lecturer = lecturer
        self.students: List[Student] = []

    def enroll_student(self, student: Student) -> bool:
        """
        Enroll student in course and ensure student.courses includes this course.
        Returns True if enrollment was performed, False if already enrolled.
        """
        if any(s.person_id == student.person_id for s in self.students):
            print(f"{student.name} already enrolled in {self.title}")
            return False
        self.students.append(student)
        student.register_course(self)  # safe: register_course only adds to student's list if needed
        print(f"{student.name} added to {self.title}")
        return True

    def display_details(self) -> None:
        lecturer_name = self.lecturer.name if self.lecturer else 'TBA'
        print(f"{self.code}: {self.title}, Credits: {self.credit_hours}, Lecturer: {lecturer_name}")
        print("Enrolled students:")
        for s in self.students:
            print(f"- {s.name}")


class Lecturer(Person):
    def __init__(self, staff_id: str, name: str, email: str, department: str):
        super().__init__(staff_id, name, email)
        self.role = "Lecturer"
        self.department = department
        self.courses: List[Course] = []

    def assign_course(self, course: Course) -> bool:
        if any(c.code == course.code for c in self.courses):
            return False
        self.courses.append(course)
        course.lecturer = self
        print(f"{self.name} assigned to {course.title}")
        return True

    def submit_grades(self, course: Course, grade: str) -> None:
        """
        Assign the same grade to every student currently enrolled in the course.
        """
        for s in course.students:
            s.grades[course.code] = grade
            print(f"Assigned grade {grade} to {s.name} for {course.code}")

    def print_summary(self) -> None:
        print(f"Lecturer: {self.name}")
        for c in self.courses:
            print(f"Teaching: {c.title} ({len(c.students)} students)")


class Registrar:
    def __init__(self):
        self.students: List[Student] = []
        self.courses: List[Course] = []
        self.lecturers: List[Lecturer] = []

    def add_student(self, s: Student) -> bool:
        if any(st.person_id == s.person_id for st in self.students):
            print(f"Student {s.name} already registered.")
            return False
        self.students.append(s)
        print(f"Added student {s.name}")
        return True

    def add_course(self, c: Course) -> bool:
        if any(course.code == c.code for course in self.courses):
            print(f"Course {c.code} already exists.")
            return False
        self.courses.append(c)
        return True

    def add_lecturer(self, l: Lecturer) -> bool:
        if any(lec.person_id == l.person_id for lec in self.lecturers):
            print(f"Lecturer {l.name} already registered.")
            return False
        self.lecturers.append(l)
        return True

    def enroll(self, student_id: str, course_code: str) -> bool:
        s = next((st for st in self.students if st.person_id == student_id), None)
        c = next((co for co in self.courses if co.code == course_code), None)
        if not s or not c:
            print("Student or course not found.")
            return False
        return c.enroll_student(s)

    def full_report(self) -> None:
        print("=== Full University Report ===")
        for c in self.courses:
            c.display_details()
        for l in self.lecturers:
            l.print_summary()
        for s in self.students:
            s.report_performance()


def main():
    reg = Registrar()

    c1 = Course("CS101", "Intro to Programming", 3)
    c2 = Course("CS201", "Data Structures", 4)

    l1 = Lecturer("L001", "Dr. Smith", "smith@uni.com", "CS")
    reg.add_lecturer(l1)

    s1 = Student("S001", "Alice", "alice@uni.com")
    s2 = Student("S002", "Bob", "bob@uni.com")
    reg.add_student(s1)
    reg.add_student(s2)

    l1.assign_course(c1)
    reg.add_course(c1)
    reg.add_course(c2)

    # use registrar.enroll to keep both sides consistent
    reg.enroll("S001", "CS101")
    reg.enroll("S002", "CS101")

    # Lecturer submits grades for the course he teaches
    l1.submit_grades(c1, "A")

    s1.attendance["CS101"] = [True, True, False, True]
    s2.attendance["CS101"] = [True, False, True, False]

    reg.full_report()

if __name__ == "__main__":
    main()
