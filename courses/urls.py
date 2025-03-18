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
    path('new-course/', views.CourseCreateView.as_view(), name='course_create'),
    path('<slug:slug>/edit/', views.CourseUpdateView.as_view(), name='course_update'),
    path('<slug:slug>/certificate/', views.certificate_view, name='certificate_view'),
    path('verify-certificate/', views.verify_certificate_view, name='verify_certificate'),
    path('course/<slug:course_slug>/attachments/', views.course_attachments, name='course_attachments'),
    path('course/<slug:course_slug>/attachments/add/', views.add_course_attachment, name='add_course_attachment'),
    path('attachment/<int:attachment_id>/edit/', views.edit_course_attachment, name='edit_course_attachment'),
    path('attachment/<int:attachment_id>/delete/', views.delete_course_attachment, name='delete_course_attachment'),
    path('attachment/<int:attachment_id>/download/', views.download_attachment, name='download_attachment'),
    path('course_modules/<int:id>', views.create_course_view, name='course_modules'),
    path('course_students/<int:id>', views.create_course_view, name='course_students'),
    path('course_analytics/<int:id>', views.create_course_view, name='course_analytics'),



]


