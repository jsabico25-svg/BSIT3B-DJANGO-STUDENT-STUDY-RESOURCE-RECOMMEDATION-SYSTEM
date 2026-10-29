from django.contrib import admin

from .models import Student


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('student_id', 'name', 'email', 'course', 'year_level')
    search_fields = ('name', 'email', 'course')
    list_filter = ('course', 'year_level')
