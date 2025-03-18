from  django import forms
from .models import Course, Module, Lesson, Quiz, Question, Comment
from django.forms import inlineformset_factory
from .models import Course, Module, Lesson, Category, CourseAttachment


class CommentForm(forms.ModelForm):
    """Form for submitting comments"""
    class Meta:
        model = Comment
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-primary focus:border-primary resize-none',
                'rows': 3,
                'placeholder': 'Faça uma pergunta ou deixe um comentário...'
            }),
        }



class CourseForm(forms.ModelForm):
    """Form for creating and editing courses"""
    
    class Meta:
        model = Course
        fields = ['title', 'slug', 'short_description', 'description', 'category', 
                  'price', 'discount_price', 'thumbnail', 'level', 'language',
                  'prerequisites', 'learning_outcomes', 'is_featured', 'is_published', 
                  'duration_in_weeks', 'tags', 'target_audience', 'certificate_available', 'end_date', 'start_date']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary focus:border-primary'}),
            'slug': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary focus:border-primary'}),
            'short_description': forms.Textarea(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary focus:border-primary', 'rows': 3}),
            'description': forms.Textarea(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary focus:border-primary', 'rows': 6}),
            'category': forms.Select(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary focus:border-primary'}),
            'price': forms.NumberInput(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary focus:border-primary', 'min': 0, 'step': 0.01}),
            'discount_price': forms.NumberInput(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary focus:border-primary', 'min': 0, 'step': 0.01}),
            'thumbnail': forms.FileInput(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary focus:border-primary'}),
            'level': forms.Select(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary focus:border-primary'}),
            'duration_in_weeks': forms.NumberInput(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary focus:border-primary', 'min': 1}),
            'language': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary focus:border-primary'}),
            'is_published': forms.CheckboxInput(attrs={'class': 'h-4 w-4 text-primary focus:ring-primary border-gray-300 rounded'}),
            'prerequisites': forms.Textarea(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary focus:border-primary', 'rows': 5}),
            'is_featured': forms.CheckboxInput(attrs={'class': 'h-4 w-4 text-primary focus:ring-primary border-gray-300 rounded'}),
            'is_published': forms.CheckboxInput(attrs={'class': 'h-4 w-4 text-primary focus:ring-primary border-gray-300 rounded'}),
            'tags': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary focus:border-primary'}),
            'learning_outcomes': forms.Textarea(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary focus:border-primary', 'rows': 3}),
            'target_audience': forms.Textarea(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary focus:border-primary', 'rows': 3}),
            'certificate_available': forms.CheckboxInput(attrs={'class': 'h-4 w-4 text-primary focus:ring-primary border-gray-300 rounded'}),
            'is_featured': forms.CheckboxInput(attrs={'class': 'h-4 w-4 text-primary focus:ring-primary border-gray-300 rounded'}),
            'end_date': forms.DateInput(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary focus:border-primary', 'type': 'date'}),
            'start_date': forms.DateInput(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary focus:border-primary', 'type': 'date'}),


        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['slug'].required = False
        self.fields['discount_price'].required = False
        self.fields['is_published'].initial = False
        self.fields['is_published'].label = "Publish immediately"
        
        # Add help texts
        self.fields['slug'].help_text = "Leave empty to auto-generate from title"
        self.fields['discount_price'].help_text = "Optional. Set a discounted price for promotions"
        self.fields['duration_in_weeks'].help_text = "Estimated duration of the course in weeks"
        
        # Add placeholders
        self.fields['title'].widget.attrs['placeholder'] = "e.g. Python for Beginners"
        self.fields['short_description'].widget.attrs['placeholder'] = "A brief overview of your course (shown in course listings)"
        self.fields['description'].widget.attrs['placeholder'] = "Detailed description of your course content and objectives"


class ModuleForm(forms.ModelForm):
    """Form for creating and editing modules"""
    
    class Meta:
        model = Module
        fields = ['title', 'description', 'order']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary focus:border-primary'}),
            'description': forms.Textarea(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary focus:border-primary', 'rows': 3}),
            'order': forms.NumberInput(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary focus:border-primary', 'min': 0}),
        }


# Create a formset for modules
ModuleFormSet = inlineformset_factory(
    Course, 
    Module, 
    form=ModuleForm,
    extra=1,
    can_delete=True
)

class CourseAttachmentForm(forms.ModelForm):
    """Form for creating and editing course attachments"""
    
    class Meta:
        model = CourseAttachment
        fields = ['title', 'description', 'file', 'file_type', 'is_free_preview', 'order']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary focus:border-primary'}),
            'description': forms.Textarea(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary focus:border-primary', 'rows': 3}),
            'file': forms.FileInput(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary focus:border-primary'}),
            'file_type': forms.Select(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary focus:border-primary'}),
            'is_free_preview': forms.CheckboxInput(attrs={'class': 'h-4 w-4 text-primary focus:ring-primary border-gray-300 rounded'}),
            'order': forms.NumberInput(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary focus:border-primary', 'min': 0}),
        }



class LessonForm(forms.ModelForm):
    class Meta:
        model = Lesson
        fields = ['title', 'content']

class QuizForm(forms.ModelForm):
    class Meta:
        model = Quiz
        fields = ['title', 'description']

class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['text', 'quiz']