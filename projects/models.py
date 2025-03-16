from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils.text import slugify
from django.urls import reverse
from accounts.models import User
from courses.models import Course

class Project(models.Model):
    """Model for student projects"""
    STATUS_CHOICES = (
        ('draft', _('Draft')),
        ('published', _('Published')),
        ('featured', _('Featured')),
    )
    
    title = models.CharField(_('Title'), max_length=200)
    slug = models.SlugField(_('Slug'), max_length=250, unique=True, blank=True)
    description = models.TextField(_('Description'))
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='projects')
    course = models.ForeignKey(
        Course, 
        on_delete=models.SET_NULL, 
        related_name='projects', 
        null=True, 
        blank=True,
        help_text=_('Associated course (optional)')
    )
    image = models.ImageField(_('Project Image'), upload_to='projects/%Y/%m/%d/', blank=True)
    repository_url = models.URLField(_('Repository URL'), blank=True)
    demo_url = models.URLField(_('Demo URL'), blank=True)
    technologies = models.CharField(_('Technologies Used'), max_length=255, help_text=_('Comma separated list of technologies'))
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)
    status = models.CharField(_('Status'), max_length=10, choices=STATUS_CHOICES, default='draft')
    is_course_project = models.BooleanField(_('Is Course Project'), default=False, help_text=_('Is this a project from the course curriculum?'))
    
    class Meta:
        verbose_name = _('Project')
        verbose_name_plural = _('Projects')
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
            # Ensure slug is unique
            original_slug = self.slug
            counter = 1
            while Project.objects.filter(slug=self.slug).exists():
                self.slug = f"{original_slug}-{counter}"
                counter += 1
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('project_detail', args=[self.slug])
    
    def get_technologies_list(self):
        """Return technologies as a list"""
        return [tech.strip() for tech in self.technologies.split(',') if tech.strip()]


class ProjectComment(models.Model):
    """Comments on projects"""
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='project_comments')
    text = models.TextField(_('Comment'))
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('Project Comment')
        verbose_name_plural = _('Project Comments')
        ordering = ['created_at']
    
    def __str__(self):
        return f'Comment by {self.user.username} on {self.project.title}'

