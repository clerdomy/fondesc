from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

class User(AbstractUser):
    """Extended user model for additional profile information"""
    bio = models.TextField(blank=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True)
    
    # User type choices
    USER_TYPE_CHOICES = (
        ('student', 'Student'),
        ('instructor', 'Instructor'),
        ('admin', 'Administrator'),
    )
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default='student')
    
    # Additional fields for instructors
    expertise = models.CharField(max_length=255, blank=True)
    
    def __str__(self):
        return self.username
    
    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')

class UserProgress(models.Model):
    """Track user progress through courses"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='progress')
    course = models.ForeignKey('courses.Course', on_delete=models.CASCADE)
    last_accessed = models.DateTimeField(auto_now=True)
    completed = models.BooleanField(default=False)
    progress_percentage = models.IntegerField(default=0)
    
    class Meta:
        unique_together = ['user', 'course']
        verbose_name = _('User Progress')
        verbose_name_plural = _('User Progress')
    
    def __str__(self):
        return f"{self.user.username}'s progress in {self.course.title}"
