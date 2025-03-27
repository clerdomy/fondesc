# -------------------------------
# Imports
# -------------------------------
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView as BaseLoginView
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from .forms import CustomUserCreationForm, UserProfileForm, NotificationSettingsForm, CustomAuthenticationForm
from .models import User, NotificationSettings
from courses.models import Enrollment, Course, UserProgress, Certificate
import logging

# -------------------------------
# Logger Configuration
# -------------------------------
# Set up a logger to capture errors, warnings, and information.
logger = logging.getLogger(__name__)

# -------------------------------
# Authentication Views
# -------------------------------

class CustomLoginView(BaseLoginView):
    """
    Custom Login view to prevent logged-in users from accessing the login page.
    """
    template_name = 'accounts/login.html'
    authentication_form = CustomAuthenticationForm  # Certifique-se de que seu formulário de autenticação personalizado está sendo usado

    def dispatch(self, request, *args, **kwargs):
        """Verifica se o usuário já está logado. Se estiver, redireciona para o painel."""
        if request.user.is_authenticated:
            messages.warning(request, "Ou deja konekte. Tanpri ale nan tablodbò a.")
            return redirect('dashboard')  # Redireciona para o painel de controle ou qualquer página que preferir
        return super().dispatch(request, *args, **kwargs)

class RegisterView(SuccessMessageMixin, CreateView):
    """User registration view, prevents logged-in users from accessing this view."""
    template_name = 'accounts/register.html'
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('login')
    success_message = "Kont ou an te kreye avèk siksè. Ou ka konekte kounye a."

    def dispatch(self, request, *args, **kwargs):
        """Prevent logged-in users from registering a new account."""
        if request.user.is_authenticated:
            messages.warning(request, "Ou deja konekte. Tanpri dekonèkte avan ou kreye yon nouvo kont.")
            return redirect('dashboard')  # Redirect to the dashboard or any other page
        return super().dispatch(request, *args, **kwargs)


class ProfileView(LoginRequiredMixin, UpdateView):
    """User profile view to update user data."""
    model = User
    form_class = UserProfileForm
    template_name = 'accounts/profile.html'
    success_url = reverse_lazy('profile')
    success_message = "Pwofil ou a te mete ajou avèk siksè."

    def get_object(self):
        """Fetch the current logged-in user."""
        return self.request.user


# -------------------------------
# Dashboard Views
# -------------------------------

@login_required
def dashboard_view(request):
    """User dashboard view, including courses, progress, and certificates."""
    try:
        # Fetch enrollments and progress data related to the logged-in user
        enrollments = Enrollment.objects.filter(user=request.user).select_related('course')
        progress_data = UserProgress.objects.filter(user=request.user).select_related('course')

        # Get certificates earned by the user
        certificates = Certificate.objects.filter(user=request.user).select_related('course')

        # Collect in-progress courses
        in_progress_courses = [
            {
                'course': enrollment.course,
                'progress': next((p.progress_percentage for p in progress_data if p.course_id == enrollment.course_id), None),
                

            }
            for enrollment in enrollments if 0 < next((p.progress_percentage for p in progress_data if p.course_id == enrollment.course_id), 0) < 100
        ]

        # Collect completed courses
        completed_courses = [p.course for p in progress_data if p.completed]

        context = {
            'enrollments_count': enrollments.count(),
            'in_progress_courses': in_progress_courses[:3],  # Show only 3 most recent
            'completed_courses': completed_courses,
            'progress_data': progress_data,
            'certificates': certificates,
            'recommended_course':Course.objects.all().order_by('-created_at')[:3],

        }
        return render(request, 'accounts/dashboard.html', context)
    
    except Exception as e:
        # Log any errors encountered
        logger.error(f"Error loading dashboard: {e}")
        messages.error(request, "Erè pandan chajman tablo a. Tanpri eseye ankò.")
        return redirect('dashboard')


@login_required
def password_change_view(request):
    """View for changing the user's password."""
    try:
        if request.method == 'POST':
            form = PasswordChangeForm(request.user, request.POST)
            if form.is_valid():
                user = form.save()
                # Update the session to prevent the user from being logged out
                update_session_auth_hash(request, user)
                messages.success(request, 'Modpas ou a te mete ajou avèk siksè!')
                return redirect('password_change')
            else:
                messages.error(request, 'Tanpri korije erè yo anba a.')
        else:
            form = PasswordChangeForm(request.user)
        
        return render(request, 'accounts/password_change.html', {'form': form})
    
    except Exception as e:
        # Log any errors encountered during password change
        logger.error(f"Error during password change: {e}")
        messages.error(request, "Erè pandan chanjman modpas. Tanpri eseye ankò.")
        return redirect('password_change')


@login_required
def notification_settings_view(request):
    """View for updating user notification preferences."""
    try:
        # Get or create notification settings for the user
        notification_settings, created = NotificationSettings.objects.get_or_create(user=request.user)
        
        if request.method == 'POST':
            form = NotificationSettingsForm(request.POST, instance=notification_settings)
            if form.is_valid():
                form.save()
                messages.success(request, 'Pefans ou nan notifikasyon yo te mete ajou avèk siksè!')
                return redirect('notification_settings')
        else:
            form = NotificationSettingsForm(instance=notification_settings)
        
        return render(request, 'accounts/notification_settings.html', {'form': form})
    
    except Exception as e:
        # Log any errors encountered during notification settings update
        logger.error(f"Error during notification settings update: {e}")
        messages.error(request, "Erè pandan mete ajou pefans notifikasyon. Tanpri eseye ankò.")
        return redirect('notification_settings')


@login_required
def my_courses_view(request):
    """View to show the user's enrolled courses and their progress."""
    try:
        enrollments = Enrollment.objects.filter(user=request.user).select_related('course')
        progress_data = UserProgress.objects.filter(user=request.user).select_related('course')

        # Combine enrollment and progress data for courses
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
    
    except Exception as e:
        # Log any errors encountered
        logger.error(f"Error loading my courses view: {e}")
        messages.error(request, "Erè pandan chajman kou yo. Tanpri eseye ankò.")
        return redirect('my_courses')


@login_required
def instructor_dashboard_view(request):
    """Instructor dashboard view, showing their courses and enrollments."""
    try:
        if request.user.user_type != 'instructor':
            messages.error(request, "Ou pa gen pèmisyon pou jwenn aksè nan tablo enstriktè a.")
            return redirect('dashboard')
        
        # Fetch the courses taught by the logged-in instructor
        courses = Course.objects.filter(instructor=request.user)
        total_enrollments = Enrollment.objects.filter(course__instructor=request.user).count()
        
        context = {
            'courses': courses,
            'total_enrollments': total_enrollments,
        }
        return render(request, 'accounts/instructor_dashboard.html', context)
    
    except Exception as e:
        # Log any errors encountered
        logger.error(f"Error loading instructor dashboard: {e}")
        messages.error(request, "Erè pandan chajman tablo enstriktè a. Tanpri eseye ankò.")
        return redirect('instructor_dashboard')


def logout_view(request):
    """Logout view to log the user out of the system."""
    try:
        # Log the user out and capture the event
        logger.info(f"User {request.user.username} logged out.")
        logout(request)
        return render(request, 'accounts/logout.html')
    
    except Exception as e:
        # Log any errors encountered during logout
        logger.error(f"Error during logout: {e}")
        messages.error(request, "Erè pandan dekonèksyon. Tanpri eseye ankò.")
        return redirect('dashboard')

