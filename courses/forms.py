from  django import forms
from .models import Course, Module, Lesson, Quiz, Question, Comment


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
    class Meta:
        model = Course
        fields = ['title', 'description', 'short_description', 'category', 'level', 'price', 'is_published']

class ModuleForm(forms.ModelForm):
    class Meta:
        model = Module
        fields = ['title', 'description']

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