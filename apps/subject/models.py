from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


# Create your models here.
class Subject(models.Model):
    subject_id = models.AutoField(primary_key=True)
    subject_name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'subjects'
        ordering = ['subject_name']

    def __str__(self):
        return self.subject_name
