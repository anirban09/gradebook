from django.contrib.auth.models import User
from django.db import models
from math import sqrt
from operator import attrgetter


# Stores the details of each course
class Course(models.Model):
    code = models.CharField(max_length=10)
    name = models.CharField(max_length=200)
    number_of_credits = models.IntegerField(default=0)
    relative_grading = models.BooleanField(default=True)
    user = models.ForeignKey(User)
    date_created = models.DateTimeField(auto_now_add=True)

    def assignments(self):
        assignments = Assignment.objects.filter(course=self)
        assignments_sorted = sorted(assignments, key=attrgetter('date_created'))
        return assignments_sorted

    def students(self):
        students = Student.objects.filter(courses__id__exact=self.id)
        students_sorted = sorted(students, key=attrgetter('id'))
        return students_sorted

    def students_marks(self):
        students = self.students()
        marks_dict = {}
        for student in students:
            marks_dict[student] = 0.0
            for assignment in self.assignments():
                marks_dict[student] += assignment.students_marks()[student]
        return marks_dict

    def average_marks(self):
        try:
            marks_sum = 0.0
            marks_list = self.students_marks()
            for student in marks_list:
                marks_sum += marks_list[student]
            return round(marks_sum/len(marks_list), 2)
        except:
            return 0.0

    def assign_grades(self):
        grades = {}
        marks = self.students_marks()
        total = 0.0
        for assignment in self.assignments():
            total += float(assignment.total_marks)
        if self.relative_grading==True:
            average = self.average_marks()
            intermediate = 0.0
            for student in marks:
                intermediate += pow(marks[student]-average, 2)
            deviation = sqrt(intermediate/len(marks))
            for student in marks:
                if marks[student] >= average+(1.5*deviation):
                    grades[student] = 'A+'
                elif marks[student] >= average+deviation:
                    grades[student] = 'A'
                elif marks[student] >= average+(0.5*deviation):
                    grades[student] = 'B+'
                elif marks[student] >= average:
                    grades[student] = 'B'
                elif marks[student] >= average-(0.5*deviation):
                    grades[student] = 'C+'
                elif marks[student] >= average-deviation:
                    grades[student] = 'C'
                elif marks[student] >= average-(1.5*deviation):
                    grades[student] = 'D'
                else:
                    grades[student] = 'F'
        else:
            for student in marks:
                if marks[student] >= 0.9*total:
                    grades[student] = 'A+'
                elif marks[student] >= 0.81*total:
                    grades[student] = 'A'
                elif marks[student] >= 0.72*total:
                    grades[student] = 'B+'
                elif marks[student] >= 0.63*total:
                    grades[student] = 'B'
                elif marks[student] >= 0.54*total:
                    grades[student] = 'C+'
                elif marks[student] >= 0.45*total:
                    grades[student] = 'C'
                elif marks[student] >= 0.35*total:
                    grades[student] = 'D'
                else:
                    grades[student] = 'F'
        return grades

    def __unicode__(self):
        return self.code+' '+self.name


# Stores the details of each assignment
class Assignment(models.Model):
    name = models.CharField(max_length=200)
    description = models.CharField(max_length=500)
    course = models.ForeignKey(Course)
    total_marks = models.DecimalField(default=0.0, max_digits=5, decimal_places=2)
    net_marks = models.DecimalField(default=0.0, max_digits=5, decimal_places=2)
    user = models.ForeignKey(User)
    date_created = models.DateTimeField(auto_now_add=True)

    def marks_factor(self):
        return float(self.net_marks)/float(self.total_marks)

    def students(self):
        return self.course.students()

    def students_marks(self):
        students_list = self.course.students()
        students_marks = {}
        for student in students_list:
            try:
                marks_obj = Marks.objects.get(course=self.course, assignment=self, student=student)
                students_marks[student] = float(marks_obj.marks)
            except:
                students_marks[student] = 0.0
        return students_marks

    def average_marks(self):
        try:
            marks_sum = 0.0
            students_marks_dict = self.students_marks()
            for student in students_marks_dict:
                marks_sum += students_marks_dict[student]
            return round(marks_sum/len(students_marks_dict), 2)
        except Exception as e:
            return e.message

    def __unicode__(self):
        return self.name+" ("+self.course.code+")"


# Stores the details of each student
class Student(models.Model):
    id = models.IntegerField(default=0, primary_key=True)
    name = models.CharField(max_length=200)
    courses = models.ManyToManyField(Course)

    def get_courses(self):
        courses = self.courses.all()
        courses_sorted = sorted(courses, key=attrgetter('code'))
        return courses_sorted

    def average_marks(self):
        courses = self.get_courses()
        total_marks = 0.0
        for course in courses:
            all_marks = Marks.objects.filter(course=course, student=self)
            for marks_object in all_marks:
                total_marks += float(marks_object.marks)
        return round(total_marks/len(courses), 2)

    def __unicode__(self):
        return str(self.id)+' '+self.name


# Stores marks details
class Marks(models.Model):
    course = models.ForeignKey(Course)
    assignment = models.ForeignKey(Assignment)
    student = models.ForeignKey(Student)
    marks = models.DecimalField(default=0.0, max_digits=5, decimal_places=2)
    date_created = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return str(float(self.marks))