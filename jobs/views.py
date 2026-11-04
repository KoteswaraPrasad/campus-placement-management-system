from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.utils import timezone
from accounts.decorators import officer_required
from .models import Job
from .forms import JobForm
from students.models import StudentProfile, Department
from applications.models import Application

@login_required
def job_list(request):
    is_officer = request.user.is_officer
    today = timezone.now().date()

    if is_officer:
        jobs = Job.objects.select_related('company').annotate(applicants_count=Count('applications')).all()
    else:
        jobs = Job.objects.select_related('company').filter(
            status='published',
            company__is_active=True
        ).annotate(applicants_count=Count('applications'))

    # Filters
    search_query = request.GET.get('q', '').strip()
    job_type = request.GET.get('job_type', '').strip()
    location = request.GET.get('location', '').strip()
    status_filter = request.GET.get('status', '').strip()
    eligible_only = request.GET.get('eligible_only') == '1'

    if search_query:
        jobs = jobs.filter(
            Q(title__icontains=search_query) |
            Q(company__name__icontains=search_query) |
            Q(required_skills__icontains=search_query) |
            Q(location__icontains=search_query)
        )

    if job_type:
        jobs = jobs.filter(job_type=job_type)

    if location:
        jobs = jobs.filter(location__icontains=location)

    if is_officer and status_filter:
        jobs = jobs.filter(status=status_filter)

    student_profile = None
    applied_job_ids = set()
    job_eligibility_map = {}

    if not is_officer and hasattr(request.user, 'student_profile'):
        student_profile = request.user.student_profile
        # Gather all job IDs student has applied to
        applied_job_ids = set(
            Application.objects.filter(student=student_profile).values_list('job_id', flat=True)
        )

        # Precompute eligibility for list
        eligible_job_ids = []
        for job in jobs:
            is_el, reasons = job.check_eligibility(student_profile)
            job_eligibility_map[job.id] = {'is_eligible': is_el, 'reasons': reasons}
            if is_el:
                eligible_job_ids.append(job.id)

        if eligible_only:
            jobs = jobs.filter(id__in=eligible_job_ids)

    paginator = Paginator(jobs, 9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Attach eligibility and applied flag to current page objects
    for job in page_obj:
        job.user_has_applied = job.id in applied_job_ids
        if student_profile and job.id in job_eligibility_map:
            job.user_is_eligible = job_eligibility_map[job.id]['is_eligible']
            job.eligibility_reasons = job_eligibility_map[job.id]['reasons']
        else:
            job.user_is_eligible = False
            job.eligibility_reasons = []

    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'selected_job_type': job_type,
        'selected_location': location,
        'status_filter': status_filter,
        'eligible_only': eligible_only,
        'job_types': Job.JOB_TYPE_CHOICES,
        'today': today,
    }
    return render(request, 'jobs/job_list.html', context)

@login_required
def job_detail(request, pk):
    job = get_object_or_404(Job.objects.select_related('company'), pk=pk)

    # Non-officers can only see published jobs from active companies
    if not request.user.is_officer:
        if job.status != 'published' or not job.company.is_active:
            messages.error(request, "This job posting is not currently available.")
            return redirect('jobs:list')

    student_profile = None
    is_eligible = False
    reasons = []
    user_application = None

    if request.user.is_student and hasattr(request.user, 'student_profile'):
        student_profile = request.user.student_profile
        is_eligible, reasons = job.check_eligibility(student_profile)
        user_application = Application.objects.filter(job=job, student=student_profile).first()

    applications = None
    if request.user.is_officer:
        applications = job.applications.select_related('student__user').all()

    return render(request, 'jobs/job_detail.html', {
        'job': job,
        'student_profile': student_profile,
        'is_eligible': is_eligible,
        'eligibility_reasons': reasons,
        'user_application': user_application,
        'applications': applications,
        'today': timezone.now().date(),
    })

@officer_required
def job_create(request):
    if request.method == 'POST':
        form = JobForm(request.POST)
        if form.is_valid():
            job = form.save(commit=False)
            job.created_by = request.user
            job.save()
            messages.success(request, f"Job '{job.title}' created successfully.")
            return redirect('jobs:detail', pk=job.pk)
        else:
            messages.error(request, "Please check the form for errors.")
    else:
        form = JobForm()

    return render(request, 'jobs/job_form.html', {'form': form, 'title': 'Create New Job Opening'})

@officer_required
def job_update(request, pk):
    job = get_object_or_404(Job, pk=pk)
    if request.method == 'POST':
        form = JobForm(request.POST, instance=job)
        if form.is_valid():
            form.save()
            messages.success(request, f"Job '{job.title}' updated successfully.")
            return redirect('jobs:detail', pk=job.pk)
        else:
            messages.error(request, "Please check the form for errors.")
    else:
        form = JobForm(instance=job)

    return render(request, 'jobs/job_form.html', {'form': form, 'job': job, 'title': f'Edit {job.title}'})

@officer_required
def job_toggle_status(request, pk):
    if request.method == 'POST':
        job = get_object_or_404(Job, pk=pk)
        new_status = request.POST.get('status')
        if new_status in dict(Job.STATUS_CHOICES):
            job.status = new_status
            job.save()
            messages.success(request, f"Job status updated to '{job.get_status_display()}'.")
        else:
            messages.error(request, "Invalid status choice.")
        return redirect('jobs:detail', pk=job.pk)
    return redirect('jobs:list')
