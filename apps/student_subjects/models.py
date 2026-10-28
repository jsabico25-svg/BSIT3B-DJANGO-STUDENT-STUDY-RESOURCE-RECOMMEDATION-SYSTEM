from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

# Create your models here.
class StudentSubject(models.Model):
    student_subject_id = models.AutoField(primary_key=True)
    student = models.ForeignKey(
        Student,
        related_name='student_subjects',
        on_delete=models.CASCADE,
    )
    subject = models.ForeignKey(
        Subject,
        related_name='student_subjects',
        on_delete=models.CASCADE,
    )
    skill_level = models.CharField(
        max_length=30,
        default='Beginner',
    )

    class Meta:
        db_table = 'student_subjects'
        constraints = [
            models.UniqueConstraint(
                fields=['student', 'subject'],
                name='unique_student_subject',
            ),
        ]

    def __str__(self):
        return f'{self.student.name} - {self.subject.subject_name}'

