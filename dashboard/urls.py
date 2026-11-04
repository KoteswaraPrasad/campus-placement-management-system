from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.home_landing, name='home'),
    path('redirect/', views.role_redirect, name='redirect'),
    path('student/', views.student_dashboard, name='student'),
    path('officer/', views.officer_dashboard, name='officer'),
    path('officer/reports/', views.officer_reports, name='reports'),
    path('officer/export/applications/', views.export_applications_csv, name='export_applications'),
    path('officer/export/placed/', views.export_placed_students_csv, name='export_placed'),
    path('officer/export/departments/', views.export_department_summary_csv, name='export_departments'),
]
