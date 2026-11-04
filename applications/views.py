from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils import timezone
from accounts.decorators import student_required, officer_required
from jobs.models import Job
from students.models import StudentProfile, Department
from notifications.models import Notification
from .models import Application, ApplicationStatus, ApplicationStatusHistory
from .forms import ApplicationApplyForm, ApplicationStatusUpdateForm

@student_required
def apply_to_job(request, job_id):
    job = get_object_or_404(Job.objects.select_related('company'), pk=job_id)
    student = getattr(request.user, 'student_profile', None)

    if not student:
        messages.error(request, "Student profile record not found. Please complete your registration.")
        return redirect('students:profile_edit')

    # 1. Check if job accepts applications
    if not job.is_active_for_applications():
        if job.is_past_deadline():
            messages.error(request, "Application deadline for this job has expired.")
        elif not job.company.is_active:
            messages.error(request, "The hiring company is currently inactive.")
        else:
            messages.error(request, "This job posting is not currently accepting applications.")
        return redirect('jobs:detail', pk=job.pk)

    # 2. Check duplicate application
    if Application.objects.filter(job=job, student=student).exists():
        messages.warning(request, "You have already submitted an application for this position.")
        return redirect('jobs:detail', pk=job.pk)

    # 3. Check student resume existence
    if not student.resume:
        messages.error(request, "Please upload your resume in your profile before applying.")
        return redirect('students:profile_edit')

    # 4. Rigorous server-side eligibility verification
    is_eligible, reasons = job.check_eligibility(student)
    if not is_eligible:
        reason_text = " ".join(reasons)
        messages.error(request, f"Application rejected: You do not meet the eligibility requirements. {reason_text}")
        return redirect('jobs:detail', pk=job.pk)

    if request.method == 'POST':
        form = ApplicationApplyForm(request.POST)
        if form.is_valid():
            application = form.save(commit=False)
            application.job = job
            application.student = student
            application.status = ApplicationStatus.APPLIED
            application.save()

            # Record initial history
            ApplicationStatusHistory.objects.create(
                application=application,
                old_status='',
                new_status=ApplicationStatus.APPLIED,
                changed_by=request.user,
                notes="Application submitted by student."
            )

            # In-app notification
            Notification.objects.create(
                recipient=request.user,
                title="Application Submitted Successfully",
                message=f"You successfully applied for '{job.title}' at {job.company.name}.",
                link=f"/applications/{application.id}/"
            )

            messages.success(request, f"Your application for '{job.title}' at {job.company.name} has been successfully submitted!")
            return redirect('applications:student_applications')
        else:
            messages.error(request, "Please check the form submission.")
    else:
        form = ApplicationApplyForm()

    return render(request, 'applications/apply.html', {'job': job, 'student': student, 'form': form})

@student_required
def student_applications(request):
    student = request.user.student_profile
    apps = Application.objects.filter(student=student).select_related('job', 'job__company')

    status_filter = request.GET.get('status', '').strip()
    if status_filter:
        apps = apps.filter(status=status_filter)

    paginator = Paginator(apps, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'applications/student_applications.html', {
        'page_obj': page_obj,
        'status_filter': status_filter,
        'statuses': ApplicationStatus.choices,
    })

@login_required
def application_detail(request, pk):
    application = get_object_or_404(
        Application.objects.select_related('job', 'job__company', 'student', 'student__user'),
        pk=pk
    )

    # Permission check: Student can only view their own; Officer can view any
    if request.user.is_student and application.student.user != request.user:
        raise PermissionDenied("You are not authorized to view this application.")

    history = application.status_history.select_related('changed_by').all()
    status_form = ApplicationStatusUpdateForm(initial={'status': application.status}) if request.user.is_officer else None

    return render(request, 'applications/application_detail.html', {
        'application': application,
        'history': history,
        'status_form': status_form,
    })

@student_required
def withdraw_application(request, pk):
    if request.method == 'POST':
        application = get_object_or_404(Application, pk=pk, student=request.user.student_profile)

        # Only allow withdrawal if in initial stages
        if application.status in [ApplicationStatus.APPLIED, ApplicationStatus.UNDER_REVIEW]:
            old_status = application.status
            application.status = ApplicationStatus.WITHDRAWN
            application.save()

            ApplicationStatusHistory.objects.create(
                application=application,
                old_status=old_status,
                new_status=ApplicationStatus.WITHDRAWN,
                changed_by=request.user,
                notes="Withdrawn by student."
            )

            messages.info(request, f"Your application for '{application.job.title}' has been withdrawn.")
        else:
            messages.error(request, f"Cannot withdraw application in '{application.status}' stage.")

        return redirect('applications:student_applications')
    return redirect('applications:student_applications')

@officer_required
def officer_application_list(request):
    apps = Application.objects.select_related('job', 'job__company', 'student', 'student__user').all()

    # Filters
    search_query = request.GET.get('q', '').strip()
    status_filter = request.GET.get('status', '').strip()
    job_filter = request.GET.get('job', '').strip()
    company_filter = request.GET.get('company', '').strip()
    dept_filter = request.GET.get('dept', '').strip()

    if search_query:
        apps = apps.filter(
            Q(student__user__first_name__icontains=search_query) |
            Q(student__user__last_name__icontains=search_query) |
            Q(student__registration_number__icontains=search_query) |
            Q(job__title__icontains=search_query) |
            Q(job__company__name__icontains=search_query)
        )

    if status_filter:
        apps = apps.filter(status=status_filter)

    if job_filter:
        apps = apps.filter(job_id=job_filter)

    if company_filter:
        apps = apps.filter(job__company_id=company_filter)

    if dept_filter:
        apps = apps.filter(student__department=dept_filter)

    paginator = Paginator(apps, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    from companies.models import Company
    companies = Company.objects.all()
    jobs = Job.objects.all()
    departments = Department.choices

    return render(request, 'applications/officer_applications.html', {
        'page_obj': page_obj,
        'search_query': search_query,
        'status_filter': status_filter,
        'job_filter': job_filter,
        'company_filter': company_filter,
        'dept_filter': dept_filter,
        'statuses': ApplicationStatus.choices,
        'companies': companies,
        'jobs': jobs,
        'departments': departments,
        'total_count': paginator.count,
    })

@officer_required
def officer_update_status(request, pk):
    if request.method == 'POST':
        application = get_object_or_404(Application, pk=pk)
        form = ApplicationStatusUpdateForm(request.POST)

        if form.is_valid():
            new_status = form.cleaned_data['status']
            notes = form.cleaned_data['notes'].strip()
            old_status = application.status

            if new_status != old_status:
                application.status = new_status
                application.save()

                # Record history
                ApplicationStatusHistory.objects.create(
                    application=application,
                    old_status=old_status,
                    new_status=new_status,
                    changed_by=request.user,
                    notes=notes
                )

                # If selected, update student placed flag
                if new_status == ApplicationStatus.SELECTED:
                    student = application.student
                    student.is_placed = True
                    student.save()

                # Send in-app notification to the candidate
                Notification.objects.create(
                    recipient=application.student.user,
                    title=f"Application Update: {new_status}",
                    message=f"Your application for '{application.job.title}' at {application.job.company.name} is now '{new_status}'. {notes}",
                    link=f"/applications/{application.id}/"
                )

                messages.success(request, f"Application status updated to '{new_status}'.")
            else:
                messages.info(request, "Status was unchanged.")

        return redirect('applications:detail', pk=application.pk)
    return redirect('applications:officer_applications')
