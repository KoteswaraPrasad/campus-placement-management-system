from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_STUDENT = 'student'
    ROLE_OFFICER = 'officer'
    ROLE_ADMIN = 'admin'

    ROLE_CHOICES = [
        (ROLE_STUDENT, 'Student'),
        (ROLE_OFFICER, 'Placement Officer'),
        (ROLE_ADMIN, 'Administrator'),
    ]

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=ROLE_STUDENT)
    email = models.EmailField(unique=True, help_text="Email address must be unique.")

    def __str__(self):
        full = self.get_full_name()
        return f"{full or self.username} ({self.get_role_display()})"

    @property
    def is_student(self):
        return self.role == self.ROLE_STUDENT

    @property
    def is_officer(self):
        return self.role == self.ROLE_OFFICER or self.is_superuser or self.is_staff

    @property
    def is_admin_role(self):
        return self.role == self.ROLE_ADMIN or self.is_superuser
