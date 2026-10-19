from django.db import models
from django.contrib.auth.models import User


class Student(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    register_number = models.CharField(
        max_length=20,
        unique=True
    )
    name = models.CharField(max_length=100)
    email = models.EmailField()
    department = models.CharField(max_length=100)
    year = models.IntegerField()

    def __str__(self):
        return f"{self.register_number} - {self.name}"


class Subject(models.Model):
    subject_code = models.CharField(
        max_length=20,
        unique=True
    )
    subject_name = models.CharField(max_length=100)
    max_marks = models.IntegerField(default=100)

    def __str__(self):
        return f"{self.subject_code} - {self.subject_name}"


class Mark(models.Model):
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE
    )
    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE
    )
    marks = models.IntegerField()

    def __str__(self):
        return f"{self.student} - {self.subject} - {self.marks}"