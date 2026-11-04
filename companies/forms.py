from django import forms
from .models import Company

class CompanyForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = [
            'name', 'industry', 'description', 'website',
            'contact_person', 'contact_email', 'contact_phone',
            'locations', 'is_active'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Google, Microsoft, TCS'}),
            'industry': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Information Technology, Financial Services'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Overview of the organization, core technologies, and culture'}),
            'website': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://example.com'}),
            'contact_person': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Recruitment Lead Name'}),
            'contact_email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'recruitment@company.com'}),
            'contact_phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+91 9876543210'}),
            'locations': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Bangalore, Hyderabad, Pune, Remote'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
