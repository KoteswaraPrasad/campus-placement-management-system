from django.db import models

class Company(models.Model):
    name = models.CharField(max_length=200, unique=True)
    industry = models.CharField(max_length=150)
    description = models.TextField()
    website = models.URLField(blank=True, null=True)
    contact_person = models.CharField(max_length=150)
    contact_email = models.EmailField()
    contact_phone = models.CharField(max_length=25, blank=True)
    locations = models.CharField(max_length=255, help_text="e.g., Bangalore, Hyderabad, Pune, Mumbai, Remote")
    is_active = models.BooleanField(default=True, help_text="Active companies can post jobs and interview students")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Companies"
        ordering = ['name']

    def __str__(self):
        return self.name

    @property
    def active_jobs_count(self):
        return self.jobs.filter(status='published').count()
