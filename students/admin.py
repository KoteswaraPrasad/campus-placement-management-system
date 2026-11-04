from django.contrib import admin
from .models import StudentProfile

@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ('registration_number', 'user', 'department', 'current_semester', 'cgpa', 'backlog_count', 'is_placed')
    list_filter = ('department', 'current_semester', 'is_placed')
    search_fields = ('registration_number', 'user__first_name', 'user__last_name', 'user__email', 'skills')
