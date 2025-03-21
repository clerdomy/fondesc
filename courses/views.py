from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.template.defaultfilters import slugify
from django.contrib import messages
from django.db.models import Q, Count, Avg
from django.http import JsonResponse, HttpResponseRedirect
from django.db.models import F
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy, reverse
from django.utils import timezone
import time
from .utils import *
from .models import Certificate


from .models import (
    Course, Module, Lesson, 
    Quiz, Question, Answer, Enrollment, 
    Category, Comment, UserProgress,
    CourseAttachment,CourseReview
)
from .forms import (
    CourseForm, ModuleForm, 
    LessonForm, QuizForm, QuestionForm, 
    CommentForm, CourseAttachmentForm,
    ModuleFormSet
)

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
            context['user_is_enrolled'] = Enrollment.objects.filter(
                user=self.request.user, 
                course=course
            ).exists()
        
        # Get course modules and lessons
        context['modules'] = Module.objects.filter(course=course).prefetch_related('lessons')
        # context['audience_items'] = course.target_audience.replace('<komanse>', '').replace('</fim>', '').split('\n')
        context['recent_reviews'] = CourseReview.objects.filter(course=course).order_by('-created_at')[:3]
        context['total_reviews'] = CourseReview.objects.filter(course=course).count()
        context['average_rating'] = rating_stars(CourseReview.objects.filter(course=course).aggregate(Avg('rating'))['rating__avg'])
        context['user_has_reviewed'] = CourseReview.objects.filter(user=self.request.user, course=course).exists()
        context['rating_distribution'] = {rating: round((CourseReview.objects.filter(course=course, rating=rating).count() / context['total_reviews']
                ) * 100 if context['total_reviews'] > 0 else 0) for rating in range(1, 6)}
        
        # Instructor info
        instructor = course.instructor
        instructor_info = {
            'total_courses': get_instructor_course(instructor),
            'total_students': get_instructor_students(instructor),
            'total_rating': get_instructor_rating(instructor),
            'total_reviews': get_instructor_reviews(instructor),
        }
        context['instructor'] = instructor_info

        # curso relacionado
        context['related_courses'] = Course.objects.filter(category=course.category).exclude(id=course.id).order_by('-created_at')[:5]

        # intructor courses
        context['instructor_courses'] = Course.objects.filter(instructor=instructor).exclude(id=course.id).order_by('-created_at')[:2]
        
        
        return context


@login_required
def add_review(request, course_slug):
    """View to add a review for a course"""
    course = get_object_or_404(Course, slug=course_slug)
    
    # Check if user is enrolled in the course
    if not Enrollment.objects.filter(user=request.user, course=course).exists():
        messages.error(request, "You must be enrolled in this course to review it.")
        return redirect('course_detail', slug=course_slug)
    
    # Check if user has already reviewed this course
    if CourseReview.objects.filter(user=request.user, course=course).exists():
        messages.error(request, "You have already reviewed this course. You can edit your existing review.")
        return redirect('edit_review', course_slug=course_slug)
    
    if request.method == 'POST':
        rating = request.POST.get('rating')
        title = request.POST.get('title')
        comment = request.POST.get('comment')
        
        if not all([rating, title, comment]):
            messages.error(request, "Please fill in all fields.")
            return render(request, 'courses/add_review.html', {'course': course})
        
        try:
            rating = int(rating)
            if rating < 1 or rating > 5:
                raise ValueError("Rating must be between 1 and 5")
        except ValueError:
            messages.error(request, "Invalid rating. Please select a rating between 1 and 5.")
            return render(request, 'courses/add_review.html', {'course': course})
        
        # Create the review
        CourseReview.objects.create(
            user=request.user,
            course=course,
            rating=rating,
            title=title,
            comment=comment
        )
        
        messages.success(request, "Your review has been submitted successfully.")
        return redirect('course_detail', slug=course_slug)
    
    return render(request, 'courses/add_review.html', {'course': course})

def edit_review(request, course_slug):
    """View to edit an existing review"""
    course = get_object_or_404(Course, slug=course_slug)
    review = get_object_or_404(CourseReview, user=request.user, course=course)
    
    if request.method == 'POST':
        rating = request.POST.get('rating')
        title = request.POST.get('title')
        comment = request.POST.get('comment')
        
        if not all([rating, title, comment]):
            messages.error(request, "Please fill in all fields.")
            return render(request, 'courses/edit_review.html', {'course': course, 'review': review})
        
        try:
            rating = int(rating)
            if rating < 1 or rating > 5:
                raise ValueError("Rating must be between 1 and 5")
        except ValueError:
            messages.error(request, "Invalid rating. Please select a rating between 1 and 5.")
            return render(request, 'courses/edit_review.html', {'course': course, 'review': review})
        
        # Update the review
        review.rating = rating
        review.title = title
        review.comment = comment
        review.save()
        
        messages.success(request, "Your review has been updated successfully.")
        return redirect('course_detail', slug=course_slug)
    
    return render(request, 'courses/edit_review.html', {'course': course, 'review': review})

@login_required
def delete_review(request, course_slug):
    """View to delete a review"""
    course = get_object_or_404(Course, slug=course_slug)
    review = get_object_or_404(CourseReview, user=request.user, course=course)
    
    if request.method == 'POST':
        review.delete()
        messages.success(request, "Your review has been deleted successfully.")
        return redirect('course_detail', slug=course_slug)
    
    return render(request, 'courses/delete_review.html', {'course': course, 'review': review})

def course_reviews(request, course_slug):
    """View to display all reviews for a course"""
    course = get_object_or_404(Course, slug=course_slug)
    reviews = course.reviews.filter(is_approved=True).order_by('-created_at')
    
    # Check if user has already reviewed this course
    user_review = None
    if request.user.is_authenticated:
        user_review = CourseReview.objects.filter(user=request.user, course=course).first()
    
    context = {
        'course': course,
        'reviews': reviews,
        'user_review': user_review,
        'rating_distribution':  10 #course.rating_distribution,
    }
    
    return render(request, 'courses/course_reviews.html', context)



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
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['module_formset'] = ModuleFormSet(self.request.POST, instance=self.object)
        else:
            context['module_formset'] = ModuleFormSet(instance=self.object)
        return context
    
    def form_valid(self, form):
        context = self.get_context_data()
        module_formset = context['module_formset']
        
        if module_formset.is_valid():
            form.instance.instructor = self.request.user
            self.object = form.save()
            module_formset.instance = self.object
            module_formset.save()
            messages.success(self.request, "Course created successfully!")
            return HttpResponseRedirect(self.get_success_url())
        else:
            return self.render_to_response(self.get_context_data(form=form))


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
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['module_formset'] = ModuleFormSet(self.request.POST, instance=self.object)
        else:
            context['module_formset'] = ModuleFormSet(instance=self.object)
        return context
    
    def form_valid(self, form):
        context = self.get_context_data()
        module_formset = context['module_formset']
        
        if module_formset.is_valid():
            self.object = form.save()
            module_formset.instance = self.object
            module_formset.save()
            
            # Process module orders if they exist
            for key, value in self.request.POST.items():
                if key.startswith('module_order_'):
                    module_id = key.replace('module_order_', '')
                    try:
                        module = Module.objects.get(id=module_id, course=self.object)
                        module.order = int(value)
                        module.save()
                    except (Module.DoesNotExist, ValueError):
                        pass
            
            messages.success(self.request, "Course updated successfully!")
            return HttpResponseRedirect(self.get_success_url())
        else:
            return self.render_to_response(self.get_context_data(form=form))


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


@login_required
def create_course_view(request):
    """View for creating a new course"""
    # Check if user is an instructor
    if not hasattr(request.user, 'instructor_profile'):
        messages.error(request, "You need to be an instructor to create courses")
        return redirect('become_instructor')
    
    if request.method == 'POST':
        form = CourseForm(request.POST, request.FILES)
        module_formset = ModuleFormSet(request.POST, prefix='modules')
        
        if form.is_valid() and module_formset.is_valid():
            # Create course but don't save to DB yet
            course = form.save(commit=False)
            course.instructor = request.user
            
            # Generate slug if not provided
            if not course.slug:
                course.slug = slugify(course.title)
            
            # Save the course
            course.save()
            
            # Save many-to-many relationships
            form.save_m2m()
            
            # Save modules
            modules = module_formset.save(commit=False)
            for module in modules:
                module.course = course
                module.save()
            
            # Delete marked modules
            for obj in module_formset.deleted_objects:
                obj.delete()
            
            messages.success(request, f"Course '{course.title}' created successfully!")
            
            if 'save_and_continue' in request.POST:
                return redirect('edit_course_modules', course_id=course.id)
            else:
                return redirect('instructor_dashboard')
    else:
        form = CourseForm()
        module_formset = ModuleFormSet(prefix='modules')
    
    context = {
        'form': form,
        'module_formset': module_formset,
        'categories': Category.objects.all(),
    }
    return render(request, 'courses/create_course.html', context)

# Adicione estas views ao arquivo

@login_required
def course_attachments(request, course_slug):
    """View to list all attachments for a course"""
    course = get_object_or_404(Course, slug=course_slug)
    
    # Check if user is instructor or enrolled
    is_instructor = request.user == course.instructor
    is_enrolled = Enrollment.objects.filter(user=request.user, course=course, is_paid=True).exists()
    
    if not (is_instructor or is_enrolled):
        # If not enrolled or instructor, only show free preview attachments
        attachments = course.attachments.filter(is_free_preview=True)
        messages.info(request, "You are viewing free preview materials. Enroll in the course to access all materials.")
    else:
        # Show all attachments
        attachments = course.attachments.all()
    
    context = {
        'course': course,
        'attachments': attachments,
        'is_instructor': is_instructor,
    }
    
    return render(request, 'courses/course_attachments.html', context)

@login_required
def add_course_attachment(request, course_slug):
    """View to add a new attachment to a course"""
    course = get_object_or_404(Course, slug=course_slug)
    
    # Only instructor can add attachments
    if request.user != course.instructor:
        messages.error(request, "You don't have permission to add attachments to this course.")
        return redirect('course_detail', slug=course_slug)
    
    if request.method == 'POST':
        form = CourseAttachmentForm(request.POST, request.FILES)
        if form.is_valid():
            attachment = form.save(commit=False)
            attachment.course = course
            attachment.save()
            messages.success(request, f"Attachment '{attachment.title}' added successfully.")
            return redirect('course_attachments', course_slug=course_slug)
    else:
        form = CourseAttachmentForm()
    
    context = {
        'course': course,
        'form': form,
    }
    
    return render(request, 'courses/add_course_attachment.html', context)

@login_required
def edit_course_attachment(request, attachment_id):
    """View to edit an existing course attachment"""
    attachment = get_object_or_404(CourseAttachment, id=attachment_id)
    course = attachment.course
    
    # Only instructor can edit attachments
    if request.user != course.instructor:
        messages.error(request, "You don't have permission to edit this attachment.")
        return redirect('course_attachments', course_slug=course.slug)
    
    if request.method == 'POST':
        form = CourseAttachmentForm(request.POST, request.FILES, instance=attachment)
        if form.is_valid():
            form.save()
            messages.success(request, f"Attachment '{attachment.title}' updated successfully.")
            return redirect('course_attachments', course_slug=course.slug)
    else:
        form = CourseAttachmentForm(instance=attachment)
    
    context = {
        'course': course,
        'attachment': attachment,
        'form': form,
    }
    
    return render(request, 'courses/edit_course_attachment.html', context)

@login_required
def delete_course_attachment(request, attachment_id):
    """View to delete a course attachment"""
    attachment = get_object_or_404(CourseAttachment, id=attachment_id)
    course = attachment.course
    
    # Only instructor can delete attachments
    if request.user != course.instructor:
        messages.error(request, "You don't have permission to delete this attachment.")
        return redirect('course_attachments', course_slug=course.slug)
    
    if request.method == 'POST':
        attachment_title = attachment.title
        attachment.delete()
        messages.success(request, f"Attachment '{attachment_title}' deleted successfully.")
        return redirect('course_attachments', course_slug=course.slug)
    
    context = {
        'course': course,
        'attachment': attachment,
    }
    
    return render(request, 'courses/delete_course_attachment.html', context)

@login_required
def download_attachment(request, attachment_id):
    """View to download a course attachment"""
    attachment = get_object_or_404(CourseAttachment, id=attachment_id)
    course = attachment.course
    
    # Check if user is instructor, enrolled, or if it's a free preview
    is_instructor = request.user == course.instructor
    is_enrolled = Enrollment.objects.filter(user=request.user, course=course, is_paid=True).exists()
    is_free_preview = attachment.is_free_preview
    
    if not (is_instructor or is_enrolled or is_free_preview):
        messages.error(request, "You need to enroll in this course to download this attachment.")
        return redirect('course_detail', slug=course.slug)
    
    # Log the download
    CourseAttachment.objects.filter(id=attachment.id).update(download_count=F('download_count') + 1)
    
    # Serve the file
    import os
    from django.http import FileResponse
    from django.utils.encoding import smart_str
    
    file_path = attachment.file.path
    response = FileResponse(open(file_path, 'rb'))
    response['Content-Disposition'] = f'attachment; filename="{smart_str(os.path.basename(file_path))}"'
    
    return response

