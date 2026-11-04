import os
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.http import FileResponse, Http404
from django.db.models import Q
from accounts.decorators import student_required, officer_required
from .models import StudentProfile, Department
from .forms import StudentProfileForm

@student_required
def student_profile_view(request):
    profile = get_object_or_404(StudentProfile, user=request.user)
    return render(request, 'students/profile.html', {'profile': profile})

@student_required
def student_profile_edit(request):
    profile = get_object_or_404(StudentProfile, user=request.user)
    if request.method == 'POST':
        form = StudentProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Your profile details have been successfully updated.")
            return redirect('students:profile')
        else:
            messages.error(request, "Please check the form for errors.")
    else:
        form = StudentProfileForm(instance=profile)

    return render(request, 'students/profile_edit.html', {'form': form, 'profile': profile})

@officer_required
def officer_student_list(request):
    students = StudentProfile.objects.select_related('user').all()

    # Filters
    search_query = request.GET.get('q', '').strip()
    dept = request.GET.get('department', '').strip()
    min_cgpa = request.GET.get('min_cgpa', '').strip()
    max_backlogs = request.GET.get('max_backlogs', '').strip()
    placement_status = request.GET.get('placement_status', '').strip()

    if search_query:
        students = students.filter(
            Q(user__first_name__icontains=search_query) |
            Q(user__last_name__icontains=search_query) |
            Q(user__email__icontains=search_query) |
            Q(registration_number__icontains=search_query) |
            Q(skills__icontains=search_query)
        )

    if dept:
        students = students.filter(department=dept)

    if min_cgpa:
        try:
            students = students.filter(cgpa__gte=float(min_cgpa))
        except ValueError:
            pass

    if max_backlogs:
        try:
            students = students.filter(backlog_count__lte=int(max_backlogs))
        except ValueError:
            pass

    if placement_status == 'placed':
        students = students.filter(is_placed=True)
    elif placement_status == 'unplaced':
        students = students.filter(is_placed=False)

    paginator = Paginator(students, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    departments = Department.choices

    context = {
        'page_obj': page_obj,
        'departments': departments,
        'selected_dept': dept,
        'search_query': search_query,
        'min_cgpa': min_cgpa,
        'max_backlogs': max_backlogs,
        'placement_status': placement_status,
        'total_count': paginator.count,
    }
    return render(request, 'students/officer_student_list.html', context)

@officer_required
def officer_student_detail(request, pk):
    profile = get_object_or_404(StudentProfile.objects.select_related('user'), pk=pk)
    applications = profile.applications.select_related('job', 'job__company').all()
    return render(request, 'students/officer_student_detail.html', {
        'student': profile,
        'applications': applications
    })

@login_required
def download_resume(request, pk):
    profile = get_object_or_404(StudentProfile, pk=pk)

    # Permission check: Only the student owner OR an officer/admin can access
    if not (request.user.is_officer or (request.user.is_student and hasattr(request.user, 'student_profile') and request.user.student_profile.pk == profile.pk)):
        raise PermissionDenied("You do not have permission to view or download this resume.")

    if not profile.resume or not os.path.exists(profile.resume.path):
        raise Http404("Resume file not found on server.")

    response = FileResponse(open(profile.resume.path, 'rb'), as_attachment=False)
    # Inline viewing if supported, or attachment
    filename = os.path.basename(profile.resume.name)
    response['Content-Disposition'] = f'inline; filename="{filename}"'
    return response
