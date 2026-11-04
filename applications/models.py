from django.db import models
from django.conf import settings
from jobs.models import Job
from students.models import StudentProfile

class ApplicationStatus(models.TextChoices):
    APPLIED = 'Applied', 'Applied'
    UNDER_REVIEW = 'Under Review', 'Under Review'
    SHORTLISTED = 'Shortlisted', 'Shortlisted'
    INTERVIEW_SCHEDULED = 'Interview Scheduled', 'Interview Scheduled'
    SELECTED = 'Selected', 'Selected'
    REJECTED = 'Rejected', 'Rejected'
    WITHDRAWN = 'Withdrawn', 'Withdrawn'

class Application(models.Model):
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='applications')
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='applications')
    status = models.CharField(
        max_length=30,
        choices=ApplicationStatus.choices,
        default=ApplicationStatus.APPLIED
    )
    cover_note = models.TextField(blank=True, help_text="Brief candidate cover note or introduction")
    applied_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('job', 'student')
        ordering = ['-applied_at']

    def __str__(self):
        return f"{self.student.user.get_full_name()} -> {self.job.title} ({self.status})"

    @property
    def badge_class(self):
        mapping = {
            ApplicationStatus.APPLIED: 'bg-primary text-white',
            ApplicationStatus.UNDER_REVIEW: 'bg-info text-dark',
            ApplicationStatus.SHORTLISTED: 'bg-warning text-dark',
            ApplicationStatus.INTERVIEW_SCHEDULED: 'bg-purple text-white',
            ApplicationStatus.SELECTED: 'bg-success text-white',
            ApplicationStatus.REJECTED: 'bg-danger text-white',
            ApplicationStatus.WITHDRAWN: 'bg-secondary text-white',
        }
        return mapping.get(self.status, 'bg-secondary text-white')

class ApplicationStatusHistory(models.Model):
    application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name='status_history')
    old_status = models.CharField(max_length=30, blank=True)
    new_status = models.CharField(max_length=30)
    changed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    notes = models.TextField(blank=True, help_text="Officer remarks or feedback")
    changed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-changed_at']

    def __str__(self):
        return f"{self.application} status: {self.old_status} -> {self.new_status}"
