from django.urls import path
from . import views

urlpatterns = [
    path('', views.CourseListView.as_view(), name='course_list'),
    path('<slug:slug>/', views.CourseDetailView.as_view(), name='course_detail'),
    path('<slug:slug>/enroll/', views.enroll_course, name='enroll_course'),
    path('<slug:slug>/learn/', views.course_learn_view, name='course_learn'),
    path('lesson/<int:lesson_id>/complete/', views.mark_lesson_complete, name='mark_lesson_complete'),
    path('quiz/<int:quiz_id>/take/', views.take_quiz_view, name='take_quiz'),
    path('courses/lesson/<int:lesson_id>/complete/', views.mark_lesson_complete, name='mark_lesson_complete'),
    # Instructor routes
    path('create/', views.CourseCreateView.as_view(), name='course_create'),
    path('<slug:slug>/edit/', views.CourseUpdateView.as_view(), name='course_update'),
    path('verify-certificate/', views.verify_certificate_view, name='verify_certificate'),
]
