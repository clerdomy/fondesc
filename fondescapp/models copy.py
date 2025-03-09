from django.db import models


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, help_text='Record creation date')
    updated_at = models.DateTimeField(auto_now=True, help_text='Record update date')
    
    class Meta:
        abstract = True

# Create your models here.
class Course_level(BaseModel):
    level = models.CharField(max_length=50)
    description = models.TextField()

    def __str__(self):
        return self.level + ' - '
    

class Meta:
        verbose_name = 'Course Level'
        verbose_name_plural = 'Course Levels'
        ordering = ['level']
        get_latest_by = 'created_at'


class CourseCategory(BaseModel):
    category = models.CharField(max_length=50, help_text='Course category')
    description = models.TextField(help_text='Course category description')

    def __str__(self):
        return self.category
    
    class Meta:
        verbose_name = 'Course Category'
        verbose_name_plural = 'Course Categories'
        ordering = ['category']
        get_latest_by = 'created_at'

class LearningObjectives(BaseModel):
    objective = models.CharField(max_length=255, help_text='Learning objective')
    
    def __str__(self):
        return self.objective

    class Meta:
        verbose_name = 'Learning Objective'
        verbose_name_plural = 'Learning Objectives'
        ordering = ['objective']
        get_latest_by = 'created_at'

class Materials(BaseModel):
    material = models.CharField(max_length=255, help_text='Material')
    description = models.TextField(help_text='Material description')


class CoursesCurriculum(BaseModel):
    title = models.CharField(max_length=255, help_text='Curriculum title')
    semester = models.ManyToManyField(Materials, help_text='First semester')   

class Course(BaseModel):
    title = models.CharField(max_length=255, help_text='Course title')
    subtitle = models.CharField(max_length=255, help_text='Course subtitle')
    description = models.TextField(help_text='Course description')
    learning_objectives = models.ManyToManyField(LearningObjectives, help_text='Course learning objectives')
    course_category = models.ForeignKey(CourseCategory, on_delete=models.CASCADE, help_text='Course category')
    course_level = models.ForeignKey(Course_level, on_delete=models.CASCADE, help_text='Course level')
    price = models.DecimalField(max_digits=10, decimal_places=2, help_text='Course price')
    curriculum = models.ManyToManyField(CoursesCurriculum, help_text='Course curriculum')
    duration = models.IntegerField(help_text='Course duration in hours')
    language = models.CharField(max_length=50, help_text='Course language')
    image = models.ImageField(upload_to='courses/', help_text='Course image')
    is_active = models.BooleanField(default=True, help_text='Course status')
    is_featured = models.BooleanField(default=False, help_text='Course featured status')

    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name = 'Course'
        verbose_name_plural = 'Courses'
        ordering = ['title']
        get_latest_by = 'created_at'

