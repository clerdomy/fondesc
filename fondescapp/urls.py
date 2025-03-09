from  django.urls import path
from fondescapp import views

urlpatterns = [
    path('', views.home, name='home-page'),
    path('kou', views.courses, name='courses-page'),
    path('kou/<str:course_type>/detay/', views.course_detail, name='course-detail-page'),
    path('sou-nou/pwofesè-yo', views.info_about_teacher, name='teacher-page'),
    path('travay-avek-nou', views.work_with_us, name='work-with-us-page'),
    path('inskripsyon', views.register, name='register-page'),
    path('sou-nou/kimoun-nou-ye', views.about, name='about-page'),
    # path('contact/', contact, name='contact-page'),

    # authentication
    path('konekte', views.login_view, name='login-page'),
    # path('logout/', views.logout, name='logout-page'),


]