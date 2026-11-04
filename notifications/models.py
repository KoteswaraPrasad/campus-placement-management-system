from django.db import models
from django.conf import settings

class Announcement(models.Model):
    CATEGORY_CHOICES = [
        ('placement_drive', 'Placement Drive'),
        ('interview_schedule', 'Interview Schedule'),
        ('new_job', 'New Job Opening'),
        ('deadline_alert', 'Deadline Alert'),
        ('general', 'General Announcement'),
    ]

    title = models.CharField(max_length=200)
    content = models.TextField()
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES, default='general')
    is_pinned = models.BooleanField(default=False, help_text="Pin to top of dashboards and list")
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-is_pinned', '-created_at']

    def __str__(self):
        return self.title

    @property
    def badge_class(self):
        mapping = {
            'placement_drive': 'bg-primary text-white',
            'interview_schedule': 'bg-info text-dark',
            'new_job': 'bg-success text-white',
            'deadline_alert': 'bg-danger text-white',
            'general': 'bg-secondary text-white',
        }
        return mapping.get(self.category, 'bg-secondary text-white')

class Notification(models.Model):
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=200)
    message = models.TextField()
    link = models.CharField(max_length=255, blank=True, help_text="Target URL e.g. /applications/1/")
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Notification for {self.recipient.username}: {self.title}"
