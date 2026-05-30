from django.db import models
from django.contrib.auth.models import User

# ==========================================
# 1. Profile Model
# ==========================================
class Profile(models.Model):
    ROLE_CHOICES = [
        ('student', 'Student'),
        ('teacher', 'Teacher'),
        ('admin', 'Admin'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='student') 
    bio = models.TextField(blank=True, null=True) 

    def __str__(self):
        return f"{self.user.username} - {self.role}"


# ==========================================
# 2. Category Model
# ==========================================
class Category(models.Model):
    name = models.CharField(max_length=100) 
    slug = models.SlugField(unique=True) 

    class Meta:
        verbose_name_plural = "Categories" 

    def __str__(self):
        return self.name


# ==========================================
# 3. Course Model
# ==========================================
class Course(models.Model):
    LEVEL_CHOICES = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    ]

    title = models.CharField(max_length=200) 
    description = models.TextField() 
    
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_courses') 
    
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='courses') 
    
    level = models.CharField(max_length=15, choices=LEVEL_CHOICES, default='beginner') 
    
    is_published = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True) 
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


# ==========================================
# 4. Enrollment Model
# ==========================================
class Enrollment(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='enrollments') 
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrolled_students') 
    enrolled_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'course')

    def __str__(self):
        return f"{self.student.username} enrolled in {self.course.title}"


# ==========================================
# 5. CourseDocument Model
# ==========================================
class CourseDocument(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='documents') 
    title = models.CharField(max_length=200) 
    file = models.FileField(upload_to='course_docs/') 
    uploaded_at = models.DateTimeField(auto_now_add=True) 

    def __str__(self):
        return f"{self.title} ({self.course.title})"