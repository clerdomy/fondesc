from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout




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

def logout_view(request):
    logout(request)
    return redirect('home-page')


