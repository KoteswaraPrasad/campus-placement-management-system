import os
from django.core.exceptions import ValidationError
from django.conf import settings

def validate_resume_file(value):
    ext = os.path.splitext(value.name)[1].lower()
    valid_extensions = ['.pdf', '.doc', '.docx']
    if ext not in valid_extensions:
        raise ValidationError(f"Unsupported file type '{ext}'. Allowed formats: PDF, DOC, DOCX.")
    
    max_size = getattr(settings, 'MAX_UPLOAD_SIZE', 5 * 1024 * 1024)
    if value.size > max_size:
        raise ValidationError(f"File size exceeds maximum allowed limit of {max_size // (1024 * 1024)}MB.")
