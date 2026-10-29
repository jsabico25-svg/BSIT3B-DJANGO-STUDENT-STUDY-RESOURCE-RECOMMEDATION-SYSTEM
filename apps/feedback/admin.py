from django.contrib import admin

from .models import Feedback


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('feedback_id', 'student', 'resource', 'rating', 'created_at')
    list_filter = ('rating', 'resource')
    search_fields = ('student__name', 'resource__title', 'comment')
