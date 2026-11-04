from django import forms
from .models import Application, ApplicationStatus

class ApplicationApplyForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ['cover_note']
        widgets = {
            'cover_note': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Share why you are interested in this position and how your skills align (Optional)...'
            })
        }

class ApplicationStatusUpdateForm(forms.Form):
    status = forms.ChoiceField(
        choices=ApplicationStatus.choices,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Add feedback, interview timing, venue, or decision notes for the candidate...'
        })
    )
