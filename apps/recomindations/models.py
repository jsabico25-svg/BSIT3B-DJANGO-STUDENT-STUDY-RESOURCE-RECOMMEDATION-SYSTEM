from django.db import models

from apps.study_resources.models import StudyResource
from apps.students.models import Student


class Recommendation(models.Model):
    recommendation_id = models.AutoField(primary_key=True)
    student = models.ForeignKey(
        Student,
        related_name='recommendations',
        on_delete=models.CASCADE,
    )
    resource = models.ForeignKey(
        StudyResource,
        related_name='recommendations',
        on_delete=models.CASCADE,
    )
    score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.00,
        null=True,
        blank=True,
    )
    recommended_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'recommendations'
        ordering = ['-recommended_at']

    def __str__(self):
        return f'{self.student.name} - {self.resource.title}'