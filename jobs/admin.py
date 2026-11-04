from django.contrib import admin
from .models import Job

@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ('title', 'company', 'job_type', 'location', 'min_cgpa', 'max_backlogs', 'salary_package', 'status', 'deadline')
    list_filter = ('status', 'job_type', 'company')
    search_fields = ('title', 'company__name', 'required_skills', 'location')
