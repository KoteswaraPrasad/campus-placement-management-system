import csv
import json
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from django.utils import timezone
from django.db.models import Count, Q
from accounts.decorators import student_required, officer_required
from students.models import StudentProfile, Department
from companies.models import Company
from jobs.models import Job
from applications.models import Application, ApplicationStatus
from notifications.models import Announcement

def home_landing(request):
    if request.user.is_authenticated:
        return redirect('dashboard:redirect')

    # Public landing statistics
    total_companies = Company.objects.filter(is_active=True).count()
    total_jobs = Job.objects.filter(status='published').count()
    total_students = StudentProfile.objects.count()
    placed_students = StudentProfile.objects.filter(is_placed=True).count()
    recent_announcements = Announcement.objects.all()[:4]

    context = {
        'total_companies': total_companies,
        'total_jobs': total_jobs,
        'total_students': total_students,
        'placed_students': placed_students,
        'recent_announcements': recent_announcements,
    }
    return render(request, 'dashboard/index.html', context)

@login_required
def role_redirect(request):
    if request.user.is_officer:
        return redirect('dashboard:officer')
    elif request.user.is_student:
        return redirect('dashboard:student')
    else:
        return redirect('admin:index')

@student_required
def student_dashboard(request):
    student = getattr(request.user, 'student_profile', None)
    if not student:
        messages.warning(request, "Please complete your student profile.")
        return redirect('students:profile_edit')

    today = timezone.now().date()
    active_jobs = Job.objects.filter(
        status='published',
        company__is_active=True,
        opening_date__lte=today,
        deadline__gte=today
    ).select_related('company')

    # Count eligible jobs
    eligible_jobs_count = 0
    for job in active_jobs:
        is_el, _ = job.check_eligibility(student)
        if is_el:
            eligible_jobs_count += 1

    # Student applications metrics
    applications = Application.objects.filter(student=student).select_related('job', 'job__company')
    total_apps = applications.count()
    under_review_count = applications.filter(status=ApplicationStatus.UNDER_REVIEW).count()
    shortlisted_count = applications.filter(status=ApplicationStatus.SHORTLISTED).count()
    selected_count = applications.filter(status=ApplicationStatus.SELECTED).count()

    recent_applications = applications.order_by('-updated_at')[:5]
    recent_announcements = Announcement.objects.all()[:5]

    context = {
        'student': student,
        'profile_completion': student.completion_percentage(),
        'available_jobs_count': active_jobs.count(),
        'eligible_jobs_count': eligible_jobs_count,
        'total_applications_count': total_apps,
        'under_review_count': under_review_count,
        'shortlisted_count': shortlisted_count,
        'selected_count': selected_count,
        'recent_applications': recent_applications,
        'recent_announcements': recent_announcements,
    }
    return render(request, 'dashboard/student_dashboard.html', context)

@officer_required
def officer_dashboard(request):
    today = timezone.now().date()

    # Metrics
    total_students = StudentProfile.objects.count()
    total_companies = Company.objects.count()
    active_companies = Company.objects.filter(is_active=True).count()
    active_jobs = Job.objects.filter(status='published', company__is_active=True, opening_date__lte=today, deadline__gte=today).count()
    total_applications = Application.objects.count()

    # Distinct placed students
    placed_students_count = StudentProfile.objects.filter(
        applications__status=ApplicationStatus.SELECTED
    ).distinct().count()

    placement_rate = round((placed_students_count / total_students * 100), 1) if total_students > 0 else 0.0

    # 1. Applications by status for Chart.js
    status_counts = Application.objects.values('status').annotate(count=Count('id'))
    status_dict = {item['status']: item['count'] for item in status_counts}
    all_statuses = [s.value for s in ApplicationStatus]
    status_chart_labels = all_statuses
    status_chart_data = [status_dict.get(s, 0) for s in all_statuses]

    # 2. Placed students by Department
    dept_placed_counts = {}
    for choice in Department.choices:
        dept_name = choice[0]
        count = StudentProfile.objects.filter(
            department=dept_name,
            applications__status=ApplicationStatus.SELECTED
        ).distinct().count()
        dept_placed_counts[dept_name] = count

    dept_chart_labels = list(dept_placed_counts.keys())
    dept_chart_data = list(dept_placed_counts.values())

    # 3. Job openings by Company
    company_job_counts = Company.objects.annotate(
        job_count=Count('jobs', filter=Q(jobs__status='published'))
    ).order_by('-job_count')[:7]

    company_chart_labels = [c.name for c in company_job_counts]
    company_chart_data = [c.job_count for c in company_job_counts]

    # Recent lists
    recent_applications = Application.objects.select_related('job', 'job__company', 'student', 'student__user').order_by('-applied_at')[:6]
    recent_jobs = Job.objects.select_related('company').order_by('-created_at')[:6]

    context = {
        'total_students': total_students,
        'total_companies': total_companies,
        'active_companies': active_companies,
        'active_jobs': active_jobs,
        'total_applications': total_applications,
        'placed_students_count': placed_students_count,
        'placement_rate': placement_rate,
        # Chart JSON
        'status_chart_labels': json.dumps(status_chart_labels),
        'status_chart_data': json.dumps(status_chart_data),
        'dept_chart_labels': json.dumps(dept_chart_labels),
        'dept_chart_data': json.dumps(dept_chart_data),
        'company_chart_labels': json.dumps(company_chart_labels),
        'company_chart_data': json.dumps(company_chart_data),
        'recent_applications': recent_applications,
        'recent_jobs': recent_jobs,
    }
    return render(request, 'dashboard/officer_dashboard.html', context)

@officer_required
def officer_reports(request):
    total_students = StudentProfile.objects.count()

    # Department breakdown
    department_summary = []
    for dept_code, dept_label in Department.choices:
        total_in_dept = StudentProfile.objects.filter(department=dept_code).count()
        placed_in_dept = StudentProfile.objects.filter(
            department=dept_code,
            applications__status=ApplicationStatus.SELECTED
        ).distinct().count()
        rate = round((placed_in_dept / total_in_dept * 100), 1) if total_in_dept > 0 else 0.0
        department_summary.append({
            'department': dept_label,
            'total_students': total_in_dept,
            'placed_students': placed_in_dept,
            'placement_rate': rate,
        })

    # Company breakdown
    company_summary = []
    companies = Company.objects.all()
    for company in companies:
        total_jobs = company.jobs.count()
        total_apps = Application.objects.filter(job__company=company).count()
        total_hires = Application.objects.filter(job__company=company, status=ApplicationStatus.SELECTED).count()
        company_summary.append({
            'company': company.name,
            'industry': company.industry,
            'total_jobs': total_jobs,
            'total_applications': total_apps,
            'total_hires': total_hires,
        })

    return render(request, 'dashboard/reports.html', {
        'department_summary': department_summary,
        'company_summary': company_summary,
        'total_students': total_students,
    })

@officer_required
def export_applications_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="placement_applications_report.csv"'

    writer = csv.writer(response)
    writer.writerow([
        'Application ID', 'Candidate Name', 'Registration No', 'Email',
        'Department', 'Current Semester', 'CGPA', 'Active Backlogs',
        'Job Title', 'Company', 'Salary Package', 'Status', 'Applied At'
    ])

    apps = Application.objects.select_related('job', 'job__company', 'student', 'student__user').all()
    for app in apps:
        writer.writerow([
            app.id,
            app.student.user.get_full_name(),
            app.student.registration_number,
            app.student.user.email,
            app.student.department,
            app.student.current_semester,
            app.student.cgpa,
            app.student.backlog_count,
            app.job.title,
            app.job.company.name,
            app.job.salary_package,
            app.status,
            app.applied_at.strftime('%Y-%m-%d %H:%M:%S'),
        ])

    return response

@officer_required
def export_placed_students_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="placed_students_report.csv"'

    writer = csv.writer(response)
    writer.writerow([
        'Student Name', 'Registration No', 'Email', 'Phone',
        'Department', 'CGPA', 'Company Name', 'Job Title', 'Salary Package'
    ])

    placed_apps = Application.objects.filter(status=ApplicationStatus.SELECTED).select_related('job', 'job__company', 'student', 'student__user')
    for app in placed_apps:
        writer.writerow([
            app.student.user.get_full_name(),
            app.student.registration_number,
            app.student.user.email,
            app.student.phone_number,
            app.student.department,
            app.student.cgpa,
            app.job.company.name,
            app.job.title,
            app.job.salary_package,
        ])

    return response

@officer_required
def export_department_summary_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="department_placement_summary.csv"'

    writer = csv.writer(response)
    writer.writerow(['Department', 'Total Registered Students', 'Placed Students', 'Placement Rate (%)'])

    for dept_code, dept_label in Department.choices:
        total = StudentProfile.objects.filter(department=dept_code).count()
        placed = StudentProfile.objects.filter(
            department=dept_code,
            applications__status=ApplicationStatus.SELECTED
        ).distinct().count()
        rate = round((placed / total * 100), 1) if total > 0 else 0.0
        writer.writerow([dept_label, total, placed, rate])

    return response
