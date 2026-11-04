from django.urls import path
from . import views

app_name = 'notifications'

urlpatterns = [
    path('announcements/', views.announcement_list, name='announcements'),
    path('announcements/create/', views.announcement_create, name='announcement_create'),
    path('announcements/<int:pk>/edit/', views.announcement_edit, name='announcement_edit'),
    path('announcements/<int:pk>/delete/', views.announcement_delete, name='announcement_delete'),
    path('', views.notification_list, name='list'),
    path('<int:pk>/read/', views.mark_notification_read, name='mark_read'),
    path('read-all/', views.mark_all_notifications_read, name='mark_all_read'),
]
