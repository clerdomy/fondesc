from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, DetailView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin

from .forms import CustomUserCreationForm, CustomAuthenticationForm, UserProfileForm
from .models import User, UserProgress
from courses.models import Enrollment, Course

class RegisterView(SuccessMessageMixin, CreateView):
    """User registration view"""
    template_name = 'accounts/register.html'
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('login')
    success_message = "Your account was created successfully. You can now log in."

class ProfileView(LoginRequiredMixin, UpdateView):
    """User profile view"""
    model = User
    form_class = UserProfileForm
    template_name = 'accounts/profile.html'
    success_url = reverse_lazy('profile')
    success_message = "Your profile was updated successfully."
    
    def get_object(self):
        return self.request.user

@login_required
def dashboard_view(request):
    """User dashboard view"""
    enrollments = Enrollment.objects.filter(user=request.user).select_related('course')
    progress_data = UserProgress.objects.filter(user=request.user).select_related('course')
    
    # Get in-progress courses
    in_progress_courses = []
    for enrollment in enrollments:
        progress = next((p for p in progress_data if p.course_id == enrollment.course_id), None)
        if progress and 0 < progress.progress_percentage < 100:
            in_progress_courses.append({
                'course': enrollment.course,
                'progress': progress.progress_percentage
            })
    
    # Get completed courses
    completed_courses = [p.course for p in progress_data if p.completed]
    
    context = {
        'enrollments_count': enrollments.count(),
        'in_progress_courses': in_progress_courses[:3],  # Show only 3 most recent
        'completed_courses': completed_courses,
        'progress_data': progress_data,
    }
    return render(request, 'accounts/dashboard.html', context)

@login_required
def my_courses_view(request):
    """View for user's enrolled courses"""
    enrollments = Enrollment.objects.filter(user=request.user).select_related('course')
    progress_data = UserProgress.objects.filter(user=request.user).select_related('course')
    
    # Combine enrollment and progress data
    courses_with_progress = []
    in_progress_exists = False
    completed_exists = False
    
    for enrollment in enrollments:
        progress = next((p for p in progress_data if p.course_id == enrollment.course_id), None)
        progress_percentage = progress.progress_percentage if progress else 0
        
        # Check if there are courses in progress
        if 0 < progress_percentage < 100:
            in_progress_exists = True
            
        # Check if there are completed courses
        if progress_percentage == 100:
            completed_exists = True
            
        courses_with_progress.append({
            'enrollment': enrollment,
            'progress': progress_percentage,
            'last_accessed': progress.last_accessed if progress else None
        })
    
    context = {
        'courses_with_progress': courses_with_progress,
        'in_progress_exists': in_progress_exists,
        'completed_exists': completed_exists
    }
    return render(request, 'accounts/my_courses.html', context)

@login_required
def instructor_dashboard_view(request):
    """Dashboard for instructors"""
    if request.user.user_type != 'instructor':
        messages.error(request, "You don't have permission to access the instructor dashboard.")
        return redirect('dashboard')
    
    courses = Course.objects.filter(instructor=request.user)
    total_enrollments = Enrollment.objects.filter(course__instructor=request.user).count()
    
    context = {
        'courses': courses,
        'total_enrollments': total_enrollments,
    }
    return render(request, 'accounts/instructor_dashboard.html', context)


def logout_view(request):
    logout(request)
    return render(request, 'accounts/logout.html')
