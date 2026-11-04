from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import PasswordChangeForm
from django.core.exceptions import ValidationError
from .models import User
from students.models import StudentProfile, Department
from students.validators import validate_resume_file

class StudentRegistrationForm(forms.ModelForm):
    # User fields
    first_name = forms.CharField(max_length=50, required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}))
    last_name = forms.CharField(max_length=50, required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}))
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'University or Personal Email'}))
    username = forms.CharField(max_length=50, required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Desired Username'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password (min 6 characters)'}), required=True)
    password_confirm = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm Password'}), required=True)

    # StudentProfile fields
    registration_number = forms.CharField(max_length=50, required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., 2022CSE042'}))
    department = forms.ChoiceField(choices=Department.choices, widget=forms.Select(attrs={'class': 'form-select'}))
    current_semester = forms.ChoiceField(choices=[(i, f"Semester {i}") for i in range(1, 9)], widget=forms.Select(attrs={'class': 'form-select'}))
    cgpa = forms.DecimalField(max_digits=4, decimal_places=2, min_value=0.0, max_value=10.0, widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 8.45', 'step': '0.01'}))
    backlog_count = forms.IntegerField(min_value=0, initial=0, widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0'}))
    phone_number = forms.CharField(max_length=20, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+91 9876543210'}))
    skills = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Python, Django, React, SQL, Problem Solving'}), help_text="Comma-separated list of your technical skills")
    resume = forms.FileField(validators=[validate_resume_file], widget=forms.ClearableFileInput(attrs={'class': 'form-control'}), help_text="Upload PDF, DOC, or DOCX (Max 5MB)")

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']

    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip().lower()
        if User.objects.filter(email=email).exists():
            raise ValidationError("A user with this email address already exists.")
        return email

    def clean_username(self):
        username = self.cleaned_data.get('username', '').strip()
        if User.objects.filter(username=username).exists():
            raise ValidationError("This username is already taken. Please choose another.")
        return username

    def clean_registration_number(self):
        reg_no = self.cleaned_data.get('registration_number', '').strip().upper()
        if StudentProfile.objects.filter(registration_number=reg_no).exists():
            raise ValidationError("This registration number is already registered.")
        return reg_no

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get('password')
        p2 = cleaned_data.get('password_confirm')
        if p1 and p2 and p1 != p2:
            self.add_error('password_confirm', "Passwords do not match.")
        if p1 and len(p1) < 6:
            self.add_error('password', "Password must be at least 6 characters long.")
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = User.ROLE_STUDENT
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
            StudentProfile.objects.create(
                user=user,
                registration_number=self.cleaned_data['registration_number'].upper(),
                department=self.cleaned_data['department'],
                current_semester=int(self.cleaned_data['current_semester']),
                cgpa=self.cleaned_data['cgpa'],
                backlog_count=self.cleaned_data['backlog_count'],
                phone_number=self.cleaned_data['phone_number'],
                skills=self.cleaned_data['skills'],
                resume=self.cleaned_data['resume'],
            )
        return user

class LoginForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username or Email', 'autofocus': True}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}))
