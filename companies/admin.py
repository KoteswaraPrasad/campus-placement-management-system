from django.contrib import admin
from .models import Company

@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'industry', 'contact_person', 'contact_email', 'locations', 'is_active', 'created_at')
    list_filter = ('is_active', 'industry')
    search_fields = ('name', 'industry', 'contact_person', 'contact_email', 'locations')
