from collections import Counter, OrderedDict
from datetime import datetime
from django.contrib import auth
from django.contrib.auth.models import User, Group
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from operator import attrgetter

from gradebook.models import Course, Assignment, Student, Marks


# def validation(username, ...):


def index(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect(reverse('grades:courses'))
    else:
        return render(request, 'gradebook/index.html', )


def register(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name', '')
        last_name = request.POST.get('last_name', '')
        email = request.POST.get('email', '')
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        level = request.POST.get('level', '')
        # Remember, validation required!
        user = User.objects.create_user(username, email, password)
        user.first_name = first_name
        user.last_name = last_name
        user.save()
        if level == 'professor':
            user.groups.add(Group.objects.get(name='Professors'))
        elif level == 'student':
            user.groups.add(Group.objects.get(name='Students'))
        real_user = auth.authenticate(username=username, password=password)
        auth.login(request, real_user)
        return HttpResponseRedirect(reverse('grades:tutorial'))
    else:
        return HttpResponseRedirect(reverse('grades:index'))


def login(request):
    if request.method == 'POST':
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        user = auth.authenticate(username=username, password=password)
        if user is not None and user.is_active:
            auth.login(request, user)
            return HttpResponseRedirect(reverse('grades:courses'))
        else:
            error_message = "You entered an incorrect username and/or password. Please try again. (Click this message to close it.)"
            context = {
            'error_message': error_message,
            }
            return render(request, 'gradebook/index.html', context)
    elif request.user.is_authenticated():
        return HttpResponseRedirect(reverse('grades:courses'))
    else:
        return HttpResponseRedirect(reverse('grades:index'))


def logout(request):
    auth.logout(request)
    return HttpResponseRedirect(reverse('grades:index'))


def courses(request):
    if request.user.is_authenticated():
        groups = request.user.groups.values_list('name', flat=True)
        if 'Students' in groups:
            name = request.user.first_name+' '+request.user.last_name
            try:
                student = Student.objects.get(name=name)
                courses = student.courses.all()
                courses_sorted = sorted(courses, key=attrgetter('code'))
                context = {
                'student': student,
                'courses': courses_sorted,
                }
                return render(request, 'gradebook/student_courses.html', context)
            except:
                error_message = "You haven't been added to Gradebook by any of your professors yet. (Click this message to close it.)"
                context = {
                'error_message': error_message,
                }
                return render(request, 'gradebook/index.html', context)
        else:
            courses = Course.objects.filter(user=request.user)
            courses_sorted = sorted(courses, key=attrgetter('code'))
            context = {
            'user': request.user,
            'courses': courses_sorted,
            }
            return render(request, 'gradebook/courses.html', context)
    else:
        HttpResponseRedirect(reverse('grades:index'))


def add_course(request):
    if request.user.is_authenticated():
        if request.method == 'POST':
            name = request.POST.get('course_name', '')
            code = request.POST.get('course_code', '')
            credits = int(request.POST.get('number_of_credits', '0'))
            grading = request.POST.get('grading', 'relative')
            if 'relative' in grading:
                relative_grading = True
            else:
                relative_grading = False
            course = Course(code=code, name=name, number_of_credits=credits, relative_grading=relative_grading, user=request.user, date_created=datetime.now())
            course.save()
            return HttpResponseRedirect(reverse('grades:add_students'))
        else:
            return render(request, 'gradebook/add_course.html', )
    else:
        return HttpResponseRedirect(reverse('grades:index'))


def course_details(request, course_id):
    if request.user.is_authenticated():
        groups = request.user.groups.values_list('name', flat=True)
        if 'Students' in groups:
            name = request.user.first_name+' '+request.user.last_name
            student = Student.objects.get(name=name)
            course = Course.objects.get(id=course_id)
            assignments = course.assignments()
            marks = {}
            percentages = {}
            for assignment in assignments:
                marks[assignment] = float(Marks.objects.get(course=course, assignment=assignment, student=student).marks)
                percentages[assignment] = round(100.0*(marks[assignment]/float(assignment.total_marks)), 2)
            context = {
            'student': student,
            'course': course,
            'assignments': assignments,
            'marks': marks,
            'percentages': percentages,
            }
            return render(request, 'gradebook/student_course_details.html', context)
        else:
            course = Course.objects.get(id=course_id)
            students = course.students()
            assignments  = course.assignments()
            students_marks = course.students_marks()
            marks_count_unordered = dict(Counter(students_marks.values()))
            marks_count_ordered = OrderedDict(sorted(marks_count_unordered.items()))
            assignment_marks = []
            for assignment in assignments:
                assignment_marks.append(assignment.students_marks())
            context = {
            'course': course,
            'students': students,
            'assignments': assignments,
            'assignment_marks': assignment_marks,
            'students_marks': students_marks,
            'marks_count': marks_count_ordered,
            }
            return render(request, 'gradebook/course_details.html', context)
    else:
        return HttpResponseRedirect(reverse('grades:index'))


def assign_grades(request, course_id):
    if request.user.is_authenticated():
        course = Course.objects.get(id=course_id)
        students = course.students()
        students_marks = course.students_marks()
        grades = course.assign_grades()
        grades_count_unordered = dict(Counter(grades.values()))
        grades_count_ordered = OrderedDict(sorted(grades_count_unordered.items()))
        context = {
        'course': course,
        'students': students,
        'students_marks': students_marks,
        'grades': grades,
        'grades_count': grades_count_ordered,
        }
        return render(request, 'gradebook/assign_grades.html', context)
    else:
        return HttpResponseRedirect(reverse('grades:index'))


def edit_course(request, course_id):
    if request.user.is_authenticated():
        course = Course.objects.get(id=course_id)
        if request.method == 'POST':
            course.code = request.POST.get('course_code', '')
            course.name = request.POST.get('course_name', '')
            course.number_of_credits = int(request.POST.get('number_of_credits', '0'))
            grading = request.POST.get('grading', '')
            if 'relative' in grading:
                course.relative_grading = True
            else:
                course.relative_grading = False
            course.save()
            return HttpResponseRedirect(reverse('grades:course_details', args=(course.id,)))
        else:
            if course.relative_grading == True:
                relgrade = True
            else:
                relgrade = False
            context = {
            'course': course,
            'relgrade': relgrade,
            }
            return render(request, 'gradebook/edit_course.html', context)
    else:
        return HttpResponseRedirect(reverse('grades:index'))


def delete_course(request, course_id):
    if request.user.is_authenticated():
        course = Course.objects.get(id=course_id)
        if request.method == 'POST':
            choice = request.POST.get('delete', '')
            if 'yes' in choice:
                course.delete()
                return HttpResponseRedirect(reverse('grades:courses'))
            else:
                return HttpResponseRedirect(reverse('grades:course_details', args=(course.id,)))
        else:
            return HttpResponseRedirect(reverse('grades:course_details', args=(course.id,)))
    else:
        return HttpResponseRedirect(reverse('grades:index'))


def students(request):
    if request.user.is_authenticated():
        courses = Course.objects.filter(user=request.user)
        students = []
        for course in courses:
            students += course.students()
        students = list(set(students))
        students_sorted = sorted(students, key=attrgetter('id'))
        average_marks = {}
        for student in students_sorted:
            average_marks[student] = student.average_marks()
        marks_count_unordered = dict(Counter(average_marks.values()))
        marks_count_ordered = OrderedDict(sorted(marks_count_unordered.items()))
        context = {
        'courses': courses,
        'students': students_sorted,
        'marks_count': marks_count_ordered,
        }
        return render(request, 'gradebook/students.html', context)
    else:
        return HttpResponseRedirect(reverse('grades:index'))


def add_students(request):
    if request.user.is_authenticated():
        if request.method == 'POST':
            course_id = int(request.POST.get('course', '0'))
            course = Course.objects.get(id=course_id)
            students = request.POST.get('list_of_students', '')
            students_list = students.splitlines()
            students_list_final = {}
            for i in range (len(students_list)):
                students_list[i] = students_list[i].split()
            try:
                for x in students_list:
                    pos = None
                    for j in range (len(x)):
                        x[j] = x[j].strip(',')
                        x[j] = x[j].strip(';')
                        x[j] = x[j].strip(':')
                        try:
                            x[j] = int(x[j])
                            pos = j
                        except:
                            pass
                        if pos is not None:
                            if pos == 0:
                                students_list_final[x[0]] = " ".join(x[1::])
                            elif pos == len(x)-1:
                                students_list_final[x[len(x)-1]] = " ".join(x[:-1:])
                for student in students_list_final:
                    try:
                        stu = Student.objects.get(id=student)
                    except:
                        stu = Student(id=student, name=students_list_final[student])
                        stu.save()
                    stu.courses.add(course)
                return HttpResponseRedirect(reverse('grades:add_assignment'))
            except:
                return render(request, 'gradebook/add_students.html', )
        else:
            try:
                courses = Course.objects.filter(user=request.user)
                ordered_courses = courses.order_by('-date_created')
            except:
                ordered_courses = []
            context = {
            'courses': ordered_courses,
            }
            return render(request, 'gradebook/add_students.html', context)
    else:
        return HttpResponseRedirect(reverse('grades:index'))


def student_details(request, student_id):
    if request.user.is_authenticated():
        student = Student.objects.get(id=student_id)
        courses = student.get_courses()
        assignments_marks = {}
        for course in courses:
            for assignment in course.assignments():
                try:
                    assignments_marks[assignment] = float(Marks.objects.get(assignment=assignment, student=student).marks)
                except:
                    pass
        percentages = {}
        for assignment in assignments_marks:
            percentages[assignment] = round(100.0*(assignments_marks[assignment]/float(assignment.total_marks)), 2)
        context = {
        'student': student,
        'courses': courses,
        'assignments_marks': assignments_marks,
        'percentages': percentages,
        }
        return render(request, 'gradebook/student_details.html', context)
    else:
        return HttpResponseRedirect(reverse('grades:index'))


def edit_student(request, student_id):
    if request.user.is_authenticated():
        student = Student.objects.get(id=student_id)
        if request.method == 'POST':
            student.id = int(request.POST.get('student_id', '0'))
            student.name = request.POST.get('student_name', '')
            student.save()
            return HttpResponseRedirect(reverse('grades:student_details', args=(student.id,)))
        else:
            context = {
            'student': student,
            }
            return render(request, 'gradebook/edit_student.html', context)
    else:
        return HttpResponseRedirect(reverse('grades:index'))


def assignments(request):
    if request.user.is_authenticated():
        courses = Course.objects.filter(user=request.user)
        assignments = Assignment.objects.filter(user=request.user)
        context = {
        'courses': courses,
        'assignments': assignments,
        }
        return render(request, 'gradebook/assignments.html', context)
    else:
        return HttpResponseRedirect(reverse('grades:index'))


def add_assignment(request):
    if request.user.is_authenticated():
        if request.method == 'POST':
            course_id = int(request.POST.get('course', ''))
            course = Course.objects.get(id=course_id)
            name = request.POST.get('assignment_name', '')
            description = request.POST.get('assignment_description', '')
            total_marks = float(request.POST.get('total_marks', '0.0'))
            net_marks = float(request.POST.get('weightage', '0.0'))
            assignment = Assignment(name=name, description=description, course=course, total_marks=total_marks, net_marks=net_marks, user=request.user, date_created=datetime.now())
            assignment.save()
            return HttpResponseRedirect(reverse('grades:add_marks', args=(assignment.id,)))
        else:
            try:
                courses = Course.objects.filter(user=request.user)
                ordered_courses = courses.order_by('-date_created')
            except:
                ordered_courses = []
            context = {
            'courses': ordered_courses,
            }
            return render(request, 'gradebook/add_assignment.html', context)
    else:
        return HttpResponseRedirect(reverse('grades:index'))


def assignment_details(request, assignment_id):
    if request.user.is_authenticated():
        assignment = Assignment.objects.get(id=assignment_id)
        course = assignment.course
        students = assignment.students()
        students_marks = assignment.students_marks()
        marks_factor = assignment.marks_factor()
        students_net_marks = {}
        for student in students_marks:
            students_net_marks[student] = students_marks[student] * marks_factor
        marks_count_unordered = dict(Counter(students_net_marks.values()))
        marks_count_ordered = OrderedDict(sorted(marks_count_unordered.items()))
        context = {
        'course': course,
        'assignment': assignment,
        'students': students,
        'students_marks': students_marks,
        'students_net_marks': students_net_marks,
        'marks_count': marks_count_ordered,
        }
        return render(request, 'gradebook/assignment_details.html', context)
    else:
        return HttpResponseRedirect(reverse('grades:index'))


def add_marks(request, assignment_id=None):
    if request.user.is_authenticated():
        if request.method == 'POST':
            course_id = int(request.POST.get('course', ''))
            course = Course.objects.get(id=course_id)
            students = course.students()
            if 'assignment' not in request.POST:
                context = {
                'courses': [course],
                'course_selected': course,
                }
                return render(request, 'gradebook/add_marks.html', context)
            else:
                assignment_id = int(request.POST.get('assignment', '0'))
                assignment = Assignment.objects.get(id=assignment_id)
                marks_entry = request.POST.get('marks_entry', '')
                marks = request.POST.get('marks', '')
                marks_per_student = {}
                if "only_marks" in marks_entry:
                    marks = marks.split()
                    for i in range (len(students)):
                        marks_per_student[students[i]] = float(marks[i])
                else:
                    marks = marks.splitlines()
                    for line in marks:
                        line_split = line.split()
                        marks_per_student[Student.objects.get(id=int(line_split[0]))] = float(line_split[1])
                for student in marks_per_student:
                    try:
                        marks_object = Marks.objects.get(course=course, assignment=assignment, student=student)
                        marks_object.marks = marks_per_student[student]
                        marks_object.save()
                    except:
                        marks_object = Marks(course=course, assignment=assignment, student=student, marks=marks_per_student[student], date_created=datetime.now())
                        marks_object.save()
                return HttpResponseRedirect(reverse('grades:index'))
        elif assignment_id is not None:
            assignment = Assignment.objects.get(id=assignment_id)
            course = assignment.course
            assignments = course.assignments()
            try:
                other_assignments = assignments.remove(assignment)
                other_assignments_sorted = sorted(other_assignments, key=attrgetter('date_created'))
                other_assignments_sorted_reverse = cother_assignments_sorted[::-1]
                final_assignments = [assignment]+other_assignments_sorted_reverse
            except:
                final_assignments = [assignment]
            context = {
            'courses': [course],
            'assignments': final_assignments,
            }
            return render(request, 'gradebook/add_marks.html', context)
        else:
            courses = Course.objects.filter(user=request.user)
            courses_sorted = sorted(courses, key=attrgetter('date_created'))
            courses_sorted_reverse = courses_sorted[::-1]
            context = {
            'courses': courses_sorted_reverse,
            }
            return render(request, 'gradebook/add_marks.html', context)
    else:
        return HttpResponseRedirect(reverse('grades:index'))


def edit_assignment(request, assignment_id):
    if request.user.is_authenticated():
        assignment = Assignment.objects.get(id=assignment_id)
        if request.method == 'POST':
            assignment.name = request.POST.get('assignment_name', '')
            assignment.description = request.POST.get('assignment_description', '')
            assignment.total_marks = float(request.POST.get('total_marks', '0.0'))
            assignment.net_marks = float(request.POST.get('weightage', '0.0'))
            assignment.save()
            return HttpResponseRedirect(reverse('grades:assignment_details', args=(assignment.id,)))
        else:
            context = {
            'assignment': assignment,
            }
            return render(request, 'gradebook/edit_assignment.html', context)
    else:
        return HttpResponseRedirect(reverse('grades:index'))


def delete_assignment(request, assignment_id):
    if request.user.is_authenticated():
        assignment = Assignment.objects.get(id=assignment_id)
        if request.method == 'POST':
            choice = request.POST.get('delete', '')
            if 'yes' in choice:
                assignment.delete()
                return HttpResponseRedirect(reverse('grades:assignments'))
            else:
                return HttpResponseRedirect(reverse('grades:assignment_details', args=(assignment.id,)))
        else:
            return HttpResponseRedirect(reverse('grades:assignment_details', args=(assignment.id,)))
    else:
        return HttpResponseRedirect(reverse('grades:index'))


def profile(request):
    if request.user.is_authenticated():
        user = request.user
        groups = user.groups.values_list('name', flat=True)
        try:
            group = str(groups[0])
        except:
            group = 'Administrators'
        context = {
        'user': user,
        'group': group,
        }
        if group == 'Students':
            return render(request, 'gradebook/profile_student.html', context)
        else:
            return render(request, 'gradebook/profile_professor.html', context)
    else:
        return HttpResponseRedirect(reverse('grades:index'))


def edit_profile(request):
    if request.user.is_authenticated():
        return HttpResponse("Edit profile.")
    else:
        return HttpResponseRedirect(reverse('grades:index'))


def tutorial(request):
    if request.user.is_authenticated():
        groups = request.user.groups.values_list('name', flat=True)
        if 'Students' in groups:
            return render(request, 'gradebook/tutorial_student.html', )
        else:
            return render(request, 'gradebook/tutorial_professor.html', )
    else:
        return HttpResponseRedirect(reverse('grades:index'))