from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('register/', views.register_student, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('password-change/', views.change_password_view, name='change_password'),
]
