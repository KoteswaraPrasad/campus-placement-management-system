from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.core.exceptions import PermissionDenied

def student_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.warning(request, "Please log in to access this page.")
            return redirect('accounts:login')
        if not request.user.is_student:
            messages.error(request, "Access restricted to students only.")
            raise PermissionDenied("Access restricted to students.")
        return view_func(request, *args, **kwargs)
    return _wrapped_view

def officer_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.warning(request, "Please log in with an authorized officer account.")
            return redirect('accounts:login')
        if not request.user.is_officer:
            messages.error(request, "Access restricted to placement officers only.")
            raise PermissionDenied("Access restricted to placement officers.")
        return view_func(request, *args, **kwargs)
    return _wrapped_view
