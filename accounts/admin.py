# yourapp/admin.py
from django.contrib import admin
from .models import User, UserProgress  # Import your models

# Optional: Customize the admin interface for User model
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'user_type', 'is_staff', 'date_joined')
    list_filter = ('user_type', 'is_staff', 'is_active')
    search_fields = ('username', 'email')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email', 'bio', 'profile_picture', 'phone_number')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('User type', {'fields': ('user_type', 'expertise')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

# Optional: Customize the admin interface for UserProgress model
@admin.register(UserProgress)
class UserProgressAdmin(admin.ModelAdmin):
    list_display = ('user', 'course', 'progress_percentage', 'completed', 'last_accessed')
    list_filter = ('completed',)
    search_fields = ('user__username', 'course__title')
    date_hierarchy = 'last_accessed'

# If you prefer a simpler registration without customization, you could just use:
# admin.site.register(User)
# admin.site.register(UserProgress)