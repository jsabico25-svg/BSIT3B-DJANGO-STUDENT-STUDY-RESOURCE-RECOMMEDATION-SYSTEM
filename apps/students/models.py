from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

# Create your models here.
class Students(models.Model):
    student_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    email = models.EmailField(max_length=100, unique=True)
    password = models.CharField(max_length=255)
    course = models.CharField(max_length=100, null=True, blank=True)
    year_level = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'students'
        ordering = ['name']

    def __str__(self):
        return self.name