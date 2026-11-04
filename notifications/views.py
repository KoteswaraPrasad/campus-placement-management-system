from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from accounts.decorators import officer_required
from .models import Announcement, Notification
from .forms import AnnouncementForm

@login_required
def announcement_list(request):
    announcements = Announcement.objects.select_related('created_by').all()
    category = request.GET.get('category', '').strip()
    if category:
        announcements = announcements.filter(category=category)

    paginator = Paginator(announcements, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'notifications/announcement_list.html', {
        'page_obj': page_obj,
        'selected_category': category,
        'categories': Announcement.CATEGORY_CHOICES,
    })

@officer_required
def announcement_create(request):
    if request.method == 'POST':
        form = AnnouncementForm(request.POST)
        if form.is_valid():
            announcement = form.save(commit=False)
            announcement.created_by = request.user
            announcement.save()
            messages.success(request, f"Announcement '{announcement.title}' published successfully.")
            return redirect('notifications:announcements')
        else:
            messages.error(request, "Please check the form for errors.")
    else:
        form = AnnouncementForm()

    return render(request, 'notifications/announcement_form.html', {'form': form, 'title': 'Create New Announcement'})

@officer_required
def announcement_edit(request, pk):
    announcement = get_object_or_404(Announcement, pk=pk)
    if request.method == 'POST':
        form = AnnouncementForm(request.POST, instance=announcement)
        if form.is_valid():
            form.save()
            messages.success(request, f"Announcement '{announcement.title}' updated successfully.")
            return redirect('notifications:announcements')
        else:
            messages.error(request, "Please check the form for errors.")
    else:
        form = AnnouncementForm(instance=announcement)

    return render(request, 'notifications/announcement_form.html', {'form': form, 'announcement': announcement, 'title': 'Edit Announcement'})

@officer_required
def announcement_delete(request, pk):
    announcement = get_object_or_404(Announcement, pk=pk)
    if request.method == 'POST':
        title = announcement.title
        announcement.delete()
        messages.success(request, f"Announcement '{title}' deleted.")
    return redirect('notifications:announcements')

@login_required
def notification_list(request):
    notifications = request.user.notifications.all()
    paginator = Paginator(notifications, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'notifications/notification_list.html', {'page_obj': page_obj})

@login_required
def mark_notification_read(request, pk):
    notification = get_object_or_404(Notification, pk=pk, recipient=request.user)
    notification.is_read = True
    notification.save()

    if notification.link:
        return redirect(notification.link)
    return redirect('notifications:list')

@login_required
def mark_all_notifications_read(request):
    request.user.notifications.filter(is_read=False).update(is_read=True)
    messages.success(request, "All notifications marked as read.")
    return redirect('notifications:list')
