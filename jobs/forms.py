from django import forms
from django.utils import timezone
from .models import Job
from companies.models import Company
from students.models import Department

class JobForm(forms.ModelForm):
    # Department multi-selection support
    dept_choices = [('ALL', 'Open to All Departments')] + list(Department.choices)
    department_selection = forms.MultipleChoiceField(
        choices=dept_choices,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        initial=['ALL'],
        help_text="Select 'Open to All Departments' or choose specific departments."
    )

    class Meta:
        model = Job
        fields = [
            'title', 'company', 'description', 'location', 'job_type',
            'required_skills', 'min_cgpa', 'max_backlogs',
            'eligible_semesters', 'salary_package', 'opening_date',
            'deadline', 'status'
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Associate Software Engineer'}),
            'company': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Full job role details, expectations, and perks'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Bangalore / Hybrid / Remote'}),
            'job_type': forms.Select(attrs={'class': 'form-select'}),
            'required_skills': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'e.g. Python, Django, REST APIs, SQL, Git'}),
            'min_cgpa': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': 'e.g. 7.00'}),
            'max_backlogs': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0'}),
            'eligible_semesters': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '7,8 or ALL'}),
            'salary_package': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 8.5 LPA or 40,000 / month'}),
            'opening_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'deadline': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['company'].queryset = Company.objects.filter(is_active=True)
        if self.instance and self.instance.pk:
            current_depts = self.instance.departments_list()
            self.fields['department_selection'].initial = current_depts

    def clean(self):
        cleaned_data = super().clean()
        opening = cleaned_data.get('opening_date')
        deadline = cleaned_data.get('deadline')
        if opening and deadline and deadline < opening:
            self.add_error('deadline', "Application deadline cannot be before the opening date.")
        return cleaned_data

    def save(self, commit=True):
        job = super().save(commit=False)
        selected_depts = self.cleaned_data.get('department_selection', [])
        if 'ALL' in selected_depts or not selected_depts:
            job.eligible_departments = 'ALL'
        else:
            job.eligible_departments = ', '.join(selected_depts)
        if commit:
            job.save()
        return job
