from django_use_email_as_username.models import BaseUser, BaseUserManager
from django.db import models
from studentLife_system.models import studentInfo

class User(BaseUser):
    objects = BaseUserManager()
    student_id = models.OneToOneField(studentInfo, on_delete=models.CASCADE, null=True, blank=True, related_name='user_student')
    user_type = models.CharField(max_length=13, choices=[('student', 'Student'), ('sao admin', 'Sao Admin'), ('medical admin', 'Medical Admin')], default='student')

    def __str__(self):
        if self.student_id:
            return f"{self.student_id.firstname} {self.student_id.lastname}"
        else:
            return self.email
