from django.contrib import admin

from .models import StudentSubject


@admin.register(StudentSubject)
class StudentSubjectAdmin(admin.ModelAdmin):
    list_display = ('student_subject_id', 'student', 'subject', 'skill_level')
    list_filter = ('subject', 'skill_level')
    search_fields = ('student__name', 'subject__subject_name')
