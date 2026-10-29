from django.contrib import admin

from .models import Recommendation


@admin.register(Recommendation)
class RecommendationAdmin(admin.ModelAdmin):
    list_display = ('recommendation_id', 'student', 'resource', 'score', 'recommended_at')
    list_filter = ('score',)
    search_fields = ('student__name', 'resource__title')
