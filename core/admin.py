from django.contrib import admin
from .models import Profile, Category, Course, Enrollment, CourseDocument

# ==========================================
# 1. (Profile)
# ==========================================
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'role', 'bio']
    list_filter = ['role']
    search_fields = ['user__username', 'bio']


# ==========================================
# 2.(Category)
# ==========================================
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}


# ==========================================
# 3. (Course) with Custom Action
# ==========================================
@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['title', 'teacher', 'category', 'level', 'is_published', 'created_at']
    list_filter = ['is_published', 'category', 'level']
    search_fields = ['title', 'description', 'teacher__username']    
    actions = ['approve_courses']

    @admin.action(description='Accept All Courses')
    def approve_courses(self, request, queryset):

        updated_count = queryset.update(is_published=True)
        self.message_user(request, f'succefully published courses {updated_count}')


# ==========================================
# 4.(Enrollment)
# ==========================================
@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ['student', 'course', 'enrolled_at']
    list_filter = ['course']
    search_fields = ['student__username', 'course__title']


# ==========================================
# 5.(CourseDocument)
# ==========================================
@admin.register(CourseDocument)
class CourseDocumentAdmin(admin.ModelAdmin):
    list_display = ['title', 'course', 'uploaded_at']
    list_filter = ['course']
    search_fields = ['title', 'course__title']