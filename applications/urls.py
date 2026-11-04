from django.urls import path
from . import views

app_name = 'applications'

urlpatterns = [
    path('apply/<int:job_id>/', views.apply_to_job, name='apply'),
    path('my-applications/', views.student_applications, name='student_applications'),
    path('<int:pk>/', views.application_detail, name='detail'),
    path('<int:pk>/withdraw/', views.withdraw_application, name='withdraw'),
    path('manage/', views.officer_application_list, name='officer_applications'),
    path('<int:pk>/update-status/', views.officer_update_status, name='officer_update_status'),
]
