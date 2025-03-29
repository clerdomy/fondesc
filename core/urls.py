"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView

urlpatterns = [
    # Admin panel route
    path('admin/', admin.site.urls),
    
    # Main application route (Fondescapp)
    path('', include('fondescapp.urls')),  
    
    # User accounts routes (translated 'accounts' to 'kont')
    path('kont/', include('accounts.urls')),  # Path for user accounts
    
    # Courses routes (translated 'courses' to 'kou')
    path('kou/', include('courses.urls')),  # Path for courses
    
    # Payments routes (translated 'payments' to 'peman')
    path('peman/', include('payments.urls')),  # Path for payments
    
    # Projects routes (translated 'projects' to 'pwojè yo')
    path('pwoje-yo/', include('projects.urls')),  # Path for projects
    
    # School registration routes (translated 'school-registration' to 'enskri-lekol')
    path('enskri-lekol/', include('school_registration.urls')),  # Path for school registration
]




if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
