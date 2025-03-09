from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from  django.contrib.auth.decorators import login_required

# Create your views here.
@login_required
def home(request):
    return render(request, 'fondescapp/index.html')

def courses(request):
    
    return render(request, 'fondescapp/courses.html')

def course_detail(request, course_type):
    return render(request, f'fondescapp/{settings.COURSE_DETAILS_PAGE[course_type]}')


def register(request):
    return render(request, 'fondescapp/registration.html')

def work_with_us(request):
    return render(request, 'fondescapp/work_with_us.html')

def contact(request):
    return render(request, 'fondescapp/contact.html')

def about(request):
    return render(request, 'fondescapp/about.html')

def info_about_teacher(request):
    return render(request, 'fondescapp/teacher.html')


# authentication

def login_view(request):

    context = {
        'title': 'Login',
        'description': 'Login to your account',
        'error': 'Usuário ou senha inválidos'
    }

    if request.user.is_authenticated:
        return redirect('home-page')
    
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home-page')
        else:
            return render(request, 'auth/login.html', context)


    return render(request, 'auth/login.html')