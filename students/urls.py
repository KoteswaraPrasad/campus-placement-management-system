from django.urls import path
from . import views

app_name = 'students'

urlpatterns = [
    path('profile/', views.student_profile_view, name='profile'),
    path('profile/edit/', views.student_profile_edit, name='profile_edit'),
    path('manage/', views.officer_student_list, name='officer_student_list'),
    path('manage/<int:pk>/', views.officer_student_detail, name='officer_student_detail'),
    path('resume/<int:pk>/', views.download_resume, name='download_resume'),
]
