from django.conf.urls import url
from gradebook import views

urlpatterns = [
    # eg: grades/
    url(r'^$', views.index, name='index'),

    url(r'^register/', views.register, name='register'),
    url(r'^login/', views.login, name='login'),
    url(r'^logout/', views.logout, name='logout'),

    url(r'^courses/$', views.courses, name='courses'),
    url(r'^courses/add/', views.add_course, name='add_course'),
    url(r'^courses/(?P<course_id>\d+)/$', views.course_details, name='course_details'),
    url(r'^courses/(?P<course_id>\d+)/grades/$', views.assign_grades, name='assign_grades'),
    url(r'^courses/(?P<course_id>\d+)/edit/$', views.edit_course, name='edit_course'),
    url(r'^courses/(?P<course_id>\d+)/delete/$', views.delete_course, name='delete_course'),

    url(r'^students/$', views.students, name='students'),
    url(r'^students/add/', views.add_students, name='add_students'),
    url(r'^students/(?P<student_id>\d+)/$', views.student_details, name='student_details'),
    url(r'^students/(?P<student_id>\d+)/edit/$', views.edit_student, name='edit_student'),

    url(r'^assignments/$', views.assignments, name='assignments'),
    url(r'^assignments/add/$', views.add_assignment, name='add_assignment'),
    url(r'^assignments/add_marks/$', views.add_marks, name='add_marks'),
    url(r'^assignments/add_marks/(?P<assignment_id>\d+)/$', views.add_marks, name='add_marks'),
    url(r'^assignments/(?P<assignment_id>\d+)/$', views.assignment_details, name='assignment_details'),
    url(r'^assignments/(?P<assignment_id>\d+)/edit/$', views.edit_assignment, name='edit_assignment'),
    url(r'^assignments/(?P<assignment_id>\d+)/delete/$', views.delete_assignment, name='delete_assignment'),

    url(r'^profile/$', views.profile, name='profile'),
    url(r'^profile/edit/$', views.edit_profile, name='edit_profile'),

    url(r'^tutorial/', views.tutorial, name='tutorial'),
]