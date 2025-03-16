from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count, Avg
from django.http import JsonResponse
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy, reverse
from django.utils import timezone
import time
from .utils import create_certificate
from .models import Certificate


from .models import (
    Course, Module, Lesson, 
    Quiz, Question, Answer, Enrollment, 
    Category, Comment, UserProgress
)
from .forms import CourseForm, ModuleForm, LessonForm, QuizForm, QuestionForm, CommentForm

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
    if Enrollment.objects.filter(user=request.user, course=course, is_paid=True).exists():
        messages.info(request, f"You are already enrolled in {course.title}")
        return redirect('course_detail', slug=slug)
    
    # Create enrollment (unpaid initially)
    enrollment, created = Enrollment.objects.get_or_create(
        user=request.user,
        course=course,
        defaults={'is_paid': False}
    )
    
    # Initialize user progress if it doesn't exist
    UserProgress.objects.get_or_create(
        user=request.user,
        course=course,
        defaults={'progress_percentage': 0}
    )
    
    # If course is free, mark as paid immediately
    if course.price <= 0:
        enrollment.is_paid = True
        enrollment.save()
        messages.success(request, f"You have successfully enrolled in {course.title}")
        return redirect('course_learn', slug=slug)
    
    # For paid courses, redirect to payment process
    messages.info(request, f"Please complete the payment to access {course.title}")
    return redirect('payment_process', course_id=course.id)

@login_required
def course_learn_view(request, slug):
    """View for learning a course"""
    course = get_object_or_404(Course, slug=slug)
    
    # Check if user is enrolled
    try:
        enrollment = Enrollment.objects.get(user=request.user, course=course)
        if not enrollment.is_paid:
            messages.info(request, "Si ou deja fè peman an, tanpri tann 1 a 2 jou pou konfimasyon. Si ou bezwen èd, kontakte nou.")
            
            return redirect('payment_process', course_id=course.id)
    except Enrollment.DoesNotExist:
        messages.error(request, "Ou bezwen enskri nan kou sa a pou ka jwenn aksè ak leson yo.")
        return redirect('course_detail', slug=slug)
    
    # Get all lessons for this course through modules
    all_lessons = []
    for module in course.modules.all().order_by('order'):
        for lesson in module.lessons.all().order_by('order'):
            all_lessons.append(lesson)
    
    # Get current module and lesson
    lesson_id = request.GET.get('lesson')
    
    if lesson_id:
        current_lesson = get_object_or_404(Lesson, id=lesson_id)
        current_module = current_lesson.module
        # Verify that the lesson belongs to this course
        if current_module.course != course:
            messages.error(request, "Leson sa a pa fè pati kou sa a.")
            return redirect('course_learn', slug=slug)
    else:
        # Default to first lesson
        if course.modules.exists():
            current_module = course.modules.order_by('order').first()
            if current_module and current_module.lessons.exists():
                current_lesson = current_module.lessons.order_by('order').first()
            else:
                messages.warning(request, "Kou sa a poko gen leson.")
                return redirect('course_detail', slug=slug)
        else:
            messages.warning(request, "Kou sa a poko gen modil.")
            return redirect('course_detail', slug=slug)
    
    # Get previous and next lessons for navigation
    if all_lessons:
        current_index = all_lessons.index(current_lesson) if current_lesson in all_lessons else 0
        prev_lesson = all_lessons[current_index - 1] if current_index > 0 else None
        next_lesson = all_lessons[current_index + 1] if current_index < len(all_lessons) - 1 else None
    else:
        prev_lesson = None
        next_lesson = None
    
    # Get or create user progress
    progress, created = UserProgress.objects.get_or_create(
        user=request.user,
        course=course
    )
    
    # Get completed lessons
    completed_lessons = list(progress.completed_lessons.all().values_list('id', flat=True))
    
    # Check if current lesson is completed
    current_lesson_completed = current_lesson.id in completed_lessons
    
    # Calculate completed lessons per module
    modules_with_progress = []
    for module in course.modules.all():
        module_lessons = module.lessons.all()
        completed_in_module = sum(1 for lesson in module_lessons if lesson.id in completed_lessons)
        module_completed = completed_in_module == module_lessons.count() and module_lessons.count() > 0
        
        modules_with_progress.append({
            'module': module,
            'completed_lessons': completed_in_module,
            'total_lessons': module_lessons.count(),
            'is_completed': module_completed
        })
    
    # Handle comment submission
    comment_form = CommentForm()
    if request.method == 'POST' and 'submit_comment' in request.POST:
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.user = request.user
            comment.lesson = current_lesson
            
            # Check if it's a reply
            parent_id = request.POST.get('parent_id')
            if parent_id:
                comment.parent = get_object_or_404(Comment, id=parent_id)
            
            comment.save()
            messages.success(request, "Komentè ou a pibliye avèk siksè!")
            return redirect(f"{request.path}?lesson={current_lesson.id}")
    
    # Get comments for current lesson
    comments = Comment.objects.filter(lesson=current_lesson, parent=None)
    
    context = {
        'course': course,
        'current_module': current_module,
        'current_lesson': current_lesson,
        'prev_lesson': prev_lesson,
        'next_lesson': next_lesson,
        'progress': progress,
        'comment_form': comment_form,
        'comments': comments,
        'completed_lessons': completed_lessons,
        'current_lesson_completed': current_lesson_completed,
        'modules_with_progress': modules_with_progress,
    }
    
    return render(request, 'courses/course_learn.html', context)

@login_required
def mark_lesson_complete(request, lesson_id):
    """Mark a lesson as complete"""
    lesson = get_object_or_404(Lesson, id=lesson_id)
    current_module = lesson.module
    course = current_module.course
    
    # Check if user is enrolled
    enrollment = get_object_or_404(Enrollment, user=request.user, course=course)
    
    # Get or create user progress
    progress, created = UserProgress.objects.get_or_create(
        user=request.user,
        course=course
    )
    
    # Mark lesson as complete
    progress.completed_lessons.add(lesson)
    
    # Calculate progress percentage
    total_lessons = 0
    for module in course.modules.all():
        total_lessons += module.lessons.count()
    
    completed_lessons = progress.completed_lessons.count()
    progress.progress_percentage = int((completed_lessons / total_lessons) * 100) if total_lessons > 0 else 0
    progress.save()
    
    messages.success(request, "Leson an make kòm fini!")
    
    # Find next lesson in the same module
    next_lesson_in_module = None
    module_lessons = list(current_module.lessons.order_by('order'))
    
    try:
        current_lesson_index = module_lessons.index(lesson)
        if current_lesson_index < len(module_lessons) - 1:
            next_lesson_in_module = module_lessons[current_lesson_index + 1]
    except ValueError:
        pass
    
    # If there's a next lesson in the same module, redirect to it
    if next_lesson_in_module:
        return redirect(f"/courses/{course.slug}/learn/?lesson={next_lesson_in_module.id}")
    
    # If we've completed all lessons in this module, find the next module
    modules = list(course.modules.order_by('order'))
    try:
        current_module_index = modules.index(current_module)
        if current_module_index < len(modules) - 1:
            next_module = modules[current_module_index + 1]
            # Get the first lesson of the next module
            first_lesson_of_next_module = next_module.lessons.order_by('order').first()
            if first_lesson_of_next_module:
                return redirect(f"/courses/{course.slug}/learn/?lesson={first_lesson_of_next_module.id}")
    except ValueError:
        pass
    
    # If this was the last lesson of the last module, check if course is 100% complete
    if progress.progress_percentage == 100:
        # Redirect to certificate page using the direct URL instead of the named URL
        return redirect(f'/courses/{course.slug}/certificate/')
    
    # If we couldn't find a next lesson or module, redirect to the course detail page
    return redirect('course_detail', slug=course.slug)


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

@login_required
def certificate_view(request, slug):
    """View for displaying a course certificate"""
    course = get_object_or_404(Course, slug=slug)
    
    # Check if user is enrolled
    try:
        enrollment = Enrollment.objects.get(user=request.user, course=course, is_paid=True)
    except Enrollment.DoesNotExist:
        messages.error(request, "Você precisa estar matriculado neste curso para acessar o certificado.")
        return redirect('course_detail', slug=slug)
    
    # Get user progress
    try:
        progress = UserProgress.objects.get(user=request.user, course=course)
    except UserProgress.DoesNotExist:
        messages.error(request, "Você precisa completar o curso para receber o certificado.")
        return redirect('course_learn', slug=slug)
    
    # Check if course is completed
    if progress.progress_percentage < 100:
        messages.error(request, "Você precisa completar 100% do curso para receber o certificado.")
        return redirect('course_learn', slug=slug)
    
    # Get or create certificate
    try:
        certificate = Certificate.objects.get(user=request.user, course=course)
    except Certificate.DoesNotExist:
        # Create a new certificate
        certificate = Certificate(user=request.user, course=course)
        certificate.save()
    
    # Registrar acesso ao certificado (opcional)
    # CertificateAccess.objects.create(certificate=certificate, ip_address=request.META.get('REMOTE_ADDR'))
    
    context = {
        'course': course,
        'certificate': certificate,
        'user': request.user,
        'issue_date': certificate.created_at.strftime("%d de %B de %Y"),
    }
    
    return render(request, 'courses/certificate.html', context)


# Adicione esta view para verificar certificados
def verify_certificate_view(request):
    """View for verifying certificate authenticity"""
    certificate_number = request.GET.get('certificate_number')
    certificate = None
    
    if certificate_number:
        try:
            certificate = Certificate.objects.get(certificate_number=certificate_number)
        except Certificate.DoesNotExist:
            pass
    
    context = {
        'certificate_number': certificate_number,
        'certificate': certificate
    }
    
    return render(request, 'courses/verify_certificate.html', context)


