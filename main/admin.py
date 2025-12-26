from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import Category, Course, Student, Enrollment


@admin.register(Category)
class CategoryAdmin(ModelAdmin):
    list_display = ('title', 'slug')
    search_fields = ('title', 'slug')
    readonly_fields = ('slug',)


@admin.register(Course)
class CourseAdmin(ModelAdmin):
    list_display = (
        'title',
        'category',
        'status',
        'price',
        'is_active',
        'created_at',
    )
    list_filter = ('category', 'status', 'is_active')
    search_fields = ('title', 'description', 'slug')
    readonly_fields = ('slug',)
    ordering = ('-created_at',)


@admin.register(Student)
class StudentAdmin(ModelAdmin):
    list_display = (
        'first_name',
        'last_name',
        'email',
        'is_active',
        'created_at',
    )
    search_fields = ('first_name', 'last_name', 'email', 'slug')
    readonly_fields = ('slug',)
    ordering = ('-created_at',)


@admin.register(Enrollment)
class EnrollmentAdmin(ModelAdmin):
    list_display = (
        'student',
        'course',
        'enrolled_at',
        'completed',
        'completed_at',
    )
    list_filter = ('completed', 'enrolled_at')
    autocomplete_fields = ('student', 'course')
