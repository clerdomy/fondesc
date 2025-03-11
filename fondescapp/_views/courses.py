from django.shortcuts import render
from django.conf import settings

def courses(request):
    return render(request, 'fondescapp/courses.html')

def course_detail(request, course_type):
    return render(request, f'fondescapp/{settings.COURSE_DETAILS_PAGE[course_type]}')
