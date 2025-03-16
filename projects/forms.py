from django import forms
from .models import Project, ProjectComment

class ProjectForm(forms.ModelForm):
    """Form for creating and editing projects"""
    class Meta:
        model = Project
        fields = ['title', 'description', 'course', 'image', 'repository_url', 
                  'demo_url', 'technologies', 'is_course_project']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 5, 'class': 'w-full px-3 py-2 border rounded-lg'}),
            'technologies': forms.TextInput(attrs={'placeholder': 'Python, Django, JavaScript, etc.'}),
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Limit course choices to enrolled courses
        if user:
            from courses.models import Enrollment
            enrolled_courses = Enrollment.objects.filter(
                user=user, 
                is_paid=True
            ).values_list('course', flat=True)
            self.fields['course'].queryset = self.fields['course'].queryset.filter(id__in=enrolled_courses)
        
        # Add Bootstrap classes to form fields
        for field_name, field in self.fields.items():
            if field_name != 'is_course_project':
                field.widget.attrs['class'] = 'w-full px-3 py-2 border rounded-lg'


class ProjectCommentForm(forms.ModelForm):
    """Form for adding comments to projects"""
    class Meta:
        model = ProjectComment
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={'rows': 3, 'class': 'w-full px-3 py-2 border rounded-lg', 'placeholder': 'Add your comment...'}),
        }

