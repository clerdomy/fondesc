from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils.text import slugify
from accounts.models import User

class Category(models.Model):
    """Course categories"""
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = _('Category')
        verbose_name_plural = _('Categories')

class Course(models.Model):
    """Main course model"""
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    short_description = models.CharField(max_length=255)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='courses')
    instructor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='courses')
    thumbnail = models.ImageField(upload_to='course_thumbnails/')
    price = models.DecimalField(max_digits=6, decimal_places=2)
    discount_price = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_published = models.BooleanField(default=False)
    duration_in_weeks = models.PositiveSmallIntegerField(default=1)
    level = models.CharField(max_length=20, choices=(
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    ))
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name = _('Course')
        verbose_name_plural = _('Courses')

class Module(models.Model):
    """Course modules/sections"""
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='modules')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['order']
        verbose_name = _('Module')
        verbose_name_plural = _('Modules')
    
    def __str__(self):
        return self.title

class Lesson(models.Model):
    """Individual lessons within modules"""
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='lessons')
    title = models.CharField(max_length=200)
    content = models.TextField()
    video_url = models.URLField(blank=True)
    order = models.PositiveIntegerField(default=0)
    duration_in_minutes = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['order']
        verbose_name = _('Lesson')
        verbose_name_plural = _('Lessons')
    
    def __str__(self):
        return self.title

class Resource(models.Model):
    """Downloadable resources for lessons"""
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='resources')
    title = models.CharField(max_length=200)
    file = models.FileField(upload_to='course_resources/')
    description = models.TextField(blank=True)
    
    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name = _('Resource')
        verbose_name_plural = _('Resources')

class Quiz(models.Model):
    """Quizzes for lessons"""
    lesson = models.OneToOneField(Lesson, on_delete=models.CASCADE, related_name='quiz')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    pass_percentage = models.PositiveIntegerField(default=70)
    
    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name = _('Quiz')
        verbose_name_plural = _('Quizzes')

class Question(models.Model):
    """Quiz questions"""
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField()
    order = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['order']
        verbose_name = _('Question')
        verbose_name_plural = _('Questions')
    
    def __str__(self):
        return self.text[:50]

class Answer(models.Model):
    """Possible answers for questions"""
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)
    
    def __str__(self):
        return self.text
    
    class Meta:
        verbose_name = _('Answer')
        verbose_name_plural = _('Answers')

class Enrollment(models.Model):
    """Course enrollments"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='enrollments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
    date_enrolled = models.DateTimeField(auto_now_add=True)
    is_paid = models.BooleanField(default=False)
    
    class Meta:
        unique_together = ['user', 'course']
        verbose_name = _('Enrollment')
        verbose_name_plural = _('Enrollments')
    
    def __str__(self):
        return f"{self.user.username} enrolled in {self.course.title}"
