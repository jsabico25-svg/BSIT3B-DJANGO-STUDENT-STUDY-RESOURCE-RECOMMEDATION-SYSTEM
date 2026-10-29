from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

from apps.study_resources.models import StudyResource
from apps.students.models import Student


class Feedback(models.Model):
    feedback_id = models.AutoField(primary_key=True)
    student = models.ForeignKey(
        Student,
        related_name='feedbacks',
        on_delete=models.CASCADE,
    )
    resource = models.ForeignKey(
        StudyResource,
        related_name='feedbacks',
        on_delete=models.CASCADE,
    )
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    comment = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'feedback'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.student.name} - {self.resource.title} ({self.rating})'