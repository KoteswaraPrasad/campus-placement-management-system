from django.contrib import admin
from .models import Application, ApplicationStatusHistory

class ApplicationStatusHistoryInline(admin.TabularInline):
    model = ApplicationStatusHistory
    extra = 0
    readonly_fields = ('old_status', 'new_status', 'changed_by', 'notes', 'changed_at')

@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('student', 'job', 'status', 'applied_at', 'updated_at')
    list_filter = ('status', 'applied_at')
    search_fields = ('student__user__first_name', 'student__user__last_name', 'student__registration_number', 'job__title')
    inlines = [ApplicationStatusHistoryInline]
