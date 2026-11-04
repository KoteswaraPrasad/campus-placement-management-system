from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from .validators import validate_resume_file

class Department(models.TextChoices):
    CSE = 'Computer Science and Engineering', 'Computer Science and Engineering'
    IT = 'Information Technology', 'Information Technology'
    ECE = 'Electronics and Communication Engineering', 'Electronics and Communication Engineering'
    EEE = 'Electrical and Electronics Engineering', 'Electrical and Electronics Engineering'
    MECH = 'Mechanical Engineering', 'Mechanical Engineering'
    CIVIL = 'Civil Engineering', 'Civil Engineering'
    AIDS = 'AI & Data Science', 'AI & Data Science'

class StudentProfile(models.Model):
    SEMESTER_CHOICES = [(i, f"Semester {i}") for i in range(1, 9)]

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='student_profile')
    registration_number = models.CharField(max_length=50, unique=True, help_text="Unique University Registration ID")
    department = models.CharField(max_length=100, choices=Department.choices)
    current_semester = models.PositiveIntegerField(choices=SEMESTER_CHOICES, default=7)
    cgpa = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        validators=[MinValueValidator(0.0), MaxValueValidator(10.0)],
        help_text="Cumulative Grade Point Average (0.00 - 10.00)"
    )
    backlog_count = models.PositiveIntegerField(default=0, help_text="Current number of active backlogs")
    phone_number = models.CharField(max_length=20, help_text="Active mobile number")
    skills = models.TextField(help_text="Comma-separated skills (e.g., Python, Django, SQL, React)")
    resume = models.FileField(upload_to='resumes/', validators=[validate_resume_file], help_text="Upload PDF, DOC, or DOCX (Max 5MB)")
    is_placed = models.BooleanField(default=False, help_text="True once selected by any participating company")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.registration_number})"

    def skills_list(self):
        if not self.skills:
            return []
        return [s.strip() for s in self.skills.split(',') if s.strip()]

    def completion_percentage(self):
        fields = [
            self.user.first_name,
            self.user.last_name,
            self.user.email,
            self.registration_number,
            self.department,
            self.current_semester,
            self.cgpa is not None,
            self.phone_number,
            self.skills,
            self.resume,
        ]
        completed = sum(1 for f in fields if f)
        return int((completed / len(fields)) * 100)
