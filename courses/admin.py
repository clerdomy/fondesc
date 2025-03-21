# yourapp/admin.py
from django.contrib import admin
from .models import (
    Category, Course, Module, Lesson, Resource,
    Quiz, Question, Answer, Enrollment, Certificate,
    Comment, UserProgress, CourseAttachment, CourseReview
)

# Optional: Customize the admin interface for UserProgress model
@admin.register(UserProgress)
class UserProgressAdmin(admin.ModelAdmin):
    list_display = ('user', 'course', 'progress_percentage', 'completed', 'last_accessed')
    list_filter = ('completed',)
    search_fields = ('user__username', 'course__title')
    date_hierarchy = 'last_accessed'

# Register the Comment model
@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('user', 'lesson', 'created_at', 'parent')
    list_filter = ('lesson__module__course', 'created_at')
    search_fields = ('text', 'user__username', 'lesson__title')
    date_hierarchy = 'created_at'



# Register Category model
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}

# Register Course model
@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'instructor', 'price', 'is_published')
    list_filter = ('is_published', 'category', 'level')
    search_fields = ('title', 'description')
    prepopulated_fields = {'slug': ('title',)}
    list_editable = ('is_published',)
    date_hierarchy = 'created_at'

# Register Module model
@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'order')
    list_filter = ('course',)
    search_fields = ('title',)
    ordering = ('course', 'order')

# Register Lesson model
@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('title', 'module', 'order', 'duration_in_minutes')
    list_filter = ('module__course',)
    search_fields = ('title',)
    ordering = ('module', 'order')

# Register Resource model
@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    list_display = ('title', 'lesson', 'file')
    list_filter = ('lesson__module__course',)
    search_fields = ('title',)

# Register Quiz model
@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ('title', 'lesson', 'pass_percentage')
    list_filter = ('lesson__module__course',)
    search_fields = ('title',)

# Register Question model
@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('text_short', 'quiz', 'order')
    list_filter = ('quiz',)
    search_fields = ('text',)
    ordering = ('quiz', 'order')
    
    def text_short(self, obj):
        return obj.text[:50]
    text_short.short_description = 'Question Text'

# Register Answer model
@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ('text', 'question', 'is_correct')
    list_filter = ('is_correct', 'question__quiz')
    search_fields = ('text',)

# Register Enrollment model
@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('user', 'course', 'date_enrolled', 'is_paid')
    list_filter = ('is_paid', 'course')
    search_fields = ('user__username', 'course__title')
    date_hierarchy = 'date_enrolled'

admin.site.register(Certificate)
admin.site.register(CourseReview)
admin.site.register(CourseAttachment)
