from django.contrib import admin

from .models import StudyResource


@admin.register(StudyResource)
class StudyResourceAdmin(admin.ModelAdmin):
    list_display = ('resource_id', 'title', 'subject', 'resource_type', 'difficulty_level')
    search_fields = ('title', 'description')
    list_filter = ('subject', 'resource_type', 'difficulty_level')
