from django.shortcuts import render

def work_with_us(request):
    return render(request, 'fondescapp/work_with_us.html')


def about(request):
    return render(request, 'fondescapp/about.html')

def info_about_teacher(request):
    return render(request, 'fondescapp/teacher.html')
