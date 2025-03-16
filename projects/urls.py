from django.urls import path
from . import views

urlpatterns = [
    path('', views.project_list, name='project_list'),
    path('my-projects/', views.my_projects, name='my_projects'),
    path('create/', views.create_project, name='create_project'),
    path('<slug:slug>/', views.project_detail, name='project_detail'),
    path('<slug:slug>/edit/', views.edit_project, name='edit_project'),
    path('<slug:slug>/delete/', views.delete_project, name='delete_project'),
    path('<slug:slug>/publish/', views.publish_project, name='publish_project'),
]

