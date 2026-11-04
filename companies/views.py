from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Count
from accounts.decorators import officer_required
from .models import Company
from .forms import CompanyForm

@login_required
def company_list(request):
    if request.user.is_officer:
        companies = Company.objects.annotate(total_jobs=Count('jobs')).all()
    else:
        # Students only see active companies
        companies = Company.objects.filter(is_active=True).annotate(total_jobs=Count('jobs'))

    search_query = request.GET.get('q', '').strip()
    status_filter = request.GET.get('status', '').strip()

    if search_query:
        companies = companies.filter(
            Q(name__icontains=search_query) |
            Q(industry__icontains=search_query) |
            Q(locations__icontains=search_query)
        )

    if request.user.is_officer and status_filter:
        if status_filter == 'active':
            companies = companies.filter(is_active=True)
        elif status_filter == 'inactive':
            companies = companies.filter(is_active=False)

    paginator = Paginator(companies, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'companies/company_list.html', {
        'page_obj': page_obj,
        'search_query': search_query,
        'status_filter': status_filter,
    })

@login_required
def company_detail(request, pk):
    company = get_object_or_404(Company, pk=pk)
    if not company.is_active and not request.user.is_officer:
        messages.error(request, "This company profile is currently inactive.")
        return redirect('companies:list')

    if request.user.is_officer:
        jobs = company.jobs.all()
    else:
        jobs = company.jobs.filter(status='published')

    return render(request, 'companies/company_detail.html', {
        'company': company,
        'jobs': jobs,
    })

@officer_required
def company_create(request):
    if request.method == 'POST':
        form = CompanyForm(request.POST)
        if form.is_valid():
            company = form.save()
            messages.success(request, f"Company '{company.name}' has been added successfully.")
            return redirect('companies:detail', pk=company.pk)
        else:
            messages.error(request, "Please correct the form errors.")
    else:
        form = CompanyForm()

    return render(request, 'companies/company_form.html', {'form': form, 'title': 'Add New Company'})

@officer_required
def company_update(request, pk):
    company = get_object_or_404(Company, pk=pk)
    if request.method == 'POST':
        form = CompanyForm(request.POST, instance=company)
        if form.is_valid():
            form.save()
            messages.success(request, f"Company '{company.name}' has been updated successfully.")
            return redirect('companies:detail', pk=company.pk)
        else:
            messages.error(request, "Please correct the form errors.")
    else:
        form = CompanyForm(instance=company)

    return render(request, 'companies/company_form.html', {'form': form, 'company': company, 'title': f'Edit {company.name}'})

@officer_required
def company_toggle_status(request, pk):
    if request.method == 'POST':
        company = get_object_or_404(Company, pk=pk)
        company.is_active = not company.is_active
        company.save()
        status_str = "activated" if company.is_active else "deactivated"
        messages.success(request, f"Company '{company.name}' has been {status_str}.")
        return redirect('companies:detail', pk=company.pk)
    return redirect('companies:list')
