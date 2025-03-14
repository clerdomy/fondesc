from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count, Avg
from django.http import JsonResponse
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy, reverse
from django.utils import timezone

from .models import Course, Module, Lesson, Quiz, Question, Answer, Enrollment, Category
from accounts.models import UserProgress
from .forms import CourseForm, ModuleForm, LessonForm, QuizForm, QuestionForm

class CourseListView(ListView):
    """View for listing all courses"""
    model = Course
    template_name = 'courses/course_list.html'
    context_object_name = 'courses'
    paginate_by = 9
    
    def get_queryset(self):
        queryset = Course.objects.filter(is_published=True)
        
        # Filter by category
        category = self.request.GET.get('category')
        if category:
            queryset = queryset.filter(category__slug=category)
        
        # Filter by level
        level = self.request.GET.get('level')
        if level:
            queryset = queryset.filter(level=level)
        
        # Search
        search_query = self.request.GET.get('q')
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(short_description__icontains=search_query)
            )
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['selected_category'] = self.request.GET.get('category')
        context['selected_level'] = self.request.GET.get('level')
        context['search_query'] = self.request.GET.get('q')
        return context

class CourseDetailView(DetailView):
    """View for course details"""
    model = Course
    template_name = 'courses/course_detail.html'
    context_object_name = 'course'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        course = self.get_object()
        
        # Check if user is enrolled
        if self.request.user.is_authenticated:
            context['is_enrolled'] = Enrollment.objects.filter(
                user=self.request.user, 
                course=course
            ).exists()
        
        # Get course modules and lessons
        context['modules'] = Module.objects.filter(course=course).prefetch_related('lessons')
        
        return context

@login_required
def enroll_course(request, slug):
    """Enroll in a course"""
    course = get_object_or_404(Course, slug=slug)
    
    # Check if already enrolled
    if Enrollment.objects.filter(user=request.user, course=course).exists():
        messages.info(request, f"You are already enrolled in {course.title}")
        return redirect('course_detail', slug=slug)
    
    # Create enrollment
    enrollment = Enrollment.objects.create(
        user=request.user,
        course=course,
        is_paid=False  # Will be updated after payment
    )
    
    # Initialize user progress
    UserProgress.objects.create(
        user=request.user,
        course=course,
        progress_percentage=0
    )
    
    messages.success(request, f"You have successfully enrolled in {course.title}")
    
    # Redirect to payment if course is not free
    if course.price > 0:
        return redirect('payment_process', enrollment_id=enrollment.id)
    else:
        enrollment.is_paid = True
        enrollment.save()
        return redirect('course_learn', slug=slug)

def course_learn_view(request, slug):
    """View for learning a course"""
    course = get_object_or_404(Course, slug=slug)
    
    # Check if user is enrolled
    enrollment = get_object_or_404(Enrollment, user=request.user, course=course)
    
    # Get course modules and lessons
    modules = Module.objects.filter(course=course).prefetch_related('lessons')
    
    # Get or create user progress
    progress, created = UserProgress.objects.get_or_create(
        user=request.user,
        course=course,
        defaults={'progress_percentage': 0}
    )
    
    # Get lesson to display (first lesson or last accessed)
    lesson_id = request.GET.get('lesson')
    if lesson_id:
        current_lesson = get_object_or_404(Lesson, id=lesson_id, module__course=course)
    else:
        # Get first lesson
        first_module = modules.first()
        if first_module:
            current_lesson = Lesson.objects.filter(module=first_module).first()
        else:
            current_lesson = None
    
    # Update last accessed
    if current_lesson:
        progress.last_accessed = timezone.now()
        progress.save()
    
    context = {
        'course': course,
        'modules': modules,
        'current_lesson': current_lesson,
        'progress': progress,
    }
    
    return render(request, 'courses/course_learn.html', context)

@login_required
def mark_lesson_complete(request, lesson_id):
    """Mark a lesson as complete"""
    if request.method == 'POST':
        lesson = get_object_or_404(Lesson, id=lesson_id)
        course = lesson.module.course
        
        # Check if user is enrolled
        enrollment = get_object_or_404(Enrollment, user=request.user, course=course)
        
        # Get user progress
        progress, created = UserProgress.objects.get_or_create(
            user=request.user,
            course=course,
            defaults={'progress_percentage': 0}
        )
        
        # Calculate new progress percentage
        total_lessons = Lesson.objects.filter(module__course=course).count()
        completed_lessons = request.session.get(f'completed_lessons_{course.id}', [])
        
        if lesson_id not in completed_lessons:
            completed_lessons.append(lesson_id)
            request.session[f'completed_lessons_{course.id}'] = completed_lessons
        
        new_progress = int((len(completed_lessons) / total_lessons) * 100)
        progress.progress_percentage = new_progress
        
        # Check if course is completed
        if new_progress >= 100:
            progress.completed = True
        
        progress.save()
        
        return JsonResponse({'success': True, 'progress': new_progress})
    
    return JsonResponse({'success': False}, status=400)

class InstructorRequiredMixin(UserPassesTestMixin):
    """Mixin to check if user is an instructor"""
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.user_type == 'instructor'

class CourseCreateView(LoginRequiredMixin, InstructorRequiredMixin, CreateView):
    """View for creating a new course"""
    model = Course
    form_class = CourseForm
    template_name = 'courses/course_form.html'
    success_url = reverse_lazy('instructor_dashboard')
    
    def form_valid(self, form):
        form.instance.instructor = self.request.user
        messages.success(self.request, "Course created successfully!")
        return super().form_valid(form)

class CourseUpdateView(LoginRequiredMixin, InstructorRequiredMixin, UpdateView):
    """View for updating a course"""
    model = Course
    form_class = CourseForm
    template_name = 'courses/course_form.html'
    
    def get_success_url(self):
        return reverse('course_detail', kwargs={'slug': self.object.slug})
    
    def get_queryset(self):
        # Only allow instructors to edit their own courses
        return Course.objects.filter(instructor=self.request.user)
    
    def form_valid(self, form):
        messages.success(self.request, "Course updated successfully!")
        return super().form_valid(form)

@login_required
def take_quiz_view(request, quiz_id):
    """View for taking a quiz"""
    quiz = get_object_or_404(Quiz, id=quiz_id)
    lesson = quiz.lesson
    course = lesson.module.course
    
    # Check if user is enrolled
    enrollment = get_object_or_404(Enrollment, user=request.user, course=course)
    
    # Get questions
    questions = Question.objects.filter(quiz=quiz).prefetch_related('answers')
    
    if request.method == 'POST':
        # Process quiz submission
        score = 0
        total_questions = questions.count()
        
        for question in questions:
            selected_answer_id = request.POST.get(f'question_{question.id}')
            if selected_answer_id:
                selected_answer = Answer.objects.get(id=selected_answer_id)
                if selected_answer.is_correct:
                    score += 1
        
        # Calculate percentage
        percentage = (score / total_questions) * 100
        passed = percentage >= quiz.pass_percentage
        
        # If passed, mark lesson as complete
        if passed:
            mark_lesson_complete(request, lesson.id)
        
        context = {
            'quiz': quiz,
            'score': score,
            'total_questions': total_questions,
            'percentage': percentage,
            'passed': passed,
            'course': course,
        }
        
        return render(request, 'courses/quiz_result.html', context)
    
    context = {
        'quiz': quiz,
        'questions': questions,
        'course': course,
    }
    
    return render(request, 'courses/take_quiz.html', context)
