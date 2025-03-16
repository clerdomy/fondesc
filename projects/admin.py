from django.contrib import admin
from .models import Project, ProjectComment

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'course', 'status', 'is_course_project', 'created_at']
    list_filter = ['status', 'is_course_project', 'created_at']
    search_fields = ['title', 'description', 'user__username', 'course__title']
    prepopulated_fields = {'slug': ('title',)}
    raw_id_fields = ['user', 'course']
    date_hierarchy = 'created_at'
    list_editable = ['status']

@admin.register(ProjectComment)
class ProjectCommentAdmin(admin.ModelAdmin):
    list_display = ['user', 'project', 'created_at']
    list_filter = ['created_at']
    search_fields = ['text', 'user__username', 'project__title']
    raw_id_fields = ['user', 'project']

