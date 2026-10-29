from django.db import models

from apps.subject.models import Subject


class StudyResource(models.Model):
    resource_id = models.AutoField(primary_key=True)
    subject = models.ForeignKey(
        Subject,
        related_name='resources',
        on_delete=models.CASCADE,
    )
    title = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    resource_type = models.CharField(
        max_length=50, null=True, blank=True
    )
    resource_url = models.URLField(
        max_length=500, null=True, blank=True
    )
    difficulty_level = models.CharField(
        max_length=30, null=True, blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'study_resources'
        ordering = ['title']

    def __str__(self):
        return self.title