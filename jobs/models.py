from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from companies.models import Company

class Job(models.Model):
    JOB_TYPE_CHOICES = [
        ('Full-time', 'Full-time'),
        ('Internship', 'Internship'),
        ('Internship+PPO', 'Internship + PPO'),
        ('Contract', 'Contract'),
    ]

    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('closed', 'Closed'),
        ('archived', 'Archived'),
    ]

    title = models.CharField(max_length=200)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='jobs')
    description = models.TextField()
    location = models.CharField(max_length=200)
    job_type = models.CharField(max_length=50, choices=JOB_TYPE_CHOICES, default='Full-time')
    required_skills = models.TextField(help_text="Comma-separated skills (e.g. Python, SQL, REST APIs)")

    # Eligibility configuration
    min_cgpa = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        default=0.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(10.0)],
        help_text="Minimum CGPA required to apply"
    )
    max_backlogs = models.PositiveIntegerField(
        default=0,
        help_text="Maximum allowed active backlogs"
    )
    eligible_departments = models.TextField(
        default="ALL",
        help_text="Comma-separated department names or 'ALL' for open to all departments"
    )
    eligible_semesters = models.CharField(
        max_length=100,
        default="7,8",
        help_text="Comma-separated semester numbers (e.g., '7,8') or 'ALL'"
    )

    salary_package = models.CharField(max_length=100, help_text="e.g., 10.5 LPA, 45,000 / month")
    opening_date = models.DateField(default=timezone.now)
    deadline = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} at {self.company.name}"

    def skills_list(self):
        if not self.required_skills:
            return []
        return [s.strip() for s in self.required_skills.split(',') if s.strip()]

    def departments_list(self):
        if not self.eligible_departments or self.eligible_departments.strip().upper() == 'ALL':
            return ['ALL']
        return [d.strip() for d in self.eligible_departments.split(',') if d.strip()]

    def semesters_list(self):
        if not self.eligible_semesters or self.eligible_semesters.strip().upper() == 'ALL':
            return ['ALL']
        return [s.strip() for s in self.eligible_semesters.split(',') if s.strip()]

    def is_active_for_applications(self):
        today = timezone.now().date()
        return (
            self.status == 'published' and
            self.company.is_active and
            self.opening_date <= today <= self.deadline
        )

    def is_past_deadline(self):
        return timezone.now().date() > self.deadline

    def check_eligibility(self, student_profile):
        """
        Server-side eligibility validation against student profile.
        Returns a tuple: (is_eligible: bool, reasons: list[str])
        """
        reasons = []
        is_eligible = True

        if not student_profile:
            return False, ["Student profile record not found."]

        # 1. CGPA check
        if student_profile.cgpa < self.min_cgpa:
            is_eligible = False
            reasons.append(
                f"Your CGPA ({student_profile.cgpa:.2f}) is below the minimum required ({self.min_cgpa:.2f})."
            )

        # 2. Backlogs check
        if student_profile.backlog_count > self.max_backlogs:
            is_eligible = False
            reasons.append(
                f"You have {student_profile.backlog_count} active backlog(s), which exceeds the maximum allowed ({self.max_backlogs})."
            )

        # 3. Department check
        dept_list = self.departments_list()
        if 'ALL' not in dept_list and student_profile.department not in dept_list:
            is_eligible = False
            reasons.append(
                f"Your department '{student_profile.department}' is not in the eligible departments list ({', '.join(dept_list)})."
            )

        # 4. Semester check
        sem_list = self.semesters_list()
        if 'ALL' not in sem_list and str(student_profile.current_semester) not in sem_list:
            is_eligible = False
            reasons.append(
                f"Your current semester ({student_profile.current_semester}) is not eligible (Eligible semesters: {', '.join(sem_list)})."
            )

        if is_eligible:
            reasons.append("You satisfy all eligibility criteria for this position.")

        return is_eligible, reasons
