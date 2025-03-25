from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'freelancer'

urlpatterns = [
    # Authentication
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('activate/<uidb64>/<token>/', views.activate_account, name='activate'),
    
    # Password reset
    path('password-reset/', views.custom_password_reset, name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='freelancer/password_reset_done.html'), 
        name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='freelancer/password_reset_confirm.html',
        success_url='/password-reset-complete/'), 
        name='password_reset_confirm'),
    path('password-reset-complete/', auth_views.PasswordResetCompleteView.as_view(
        template_name='freelancer/password_reset_complete.html'), 
        name='password_reset_complete'),
    
    # Dashboard and Profile
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/', views.profile, name='profile'),
    path('eligibility-form/', views.eligibility_form, name='eligibility_form'),
    
    # Work Items
    path('works/', views.work_list, name='work_list'),
    path('works/<slug:slug>/', views.work_detail, name='work_detail'),
    path('works/<slug:slug>/select/', views.work_select, name='work_select'),
    path('works/<slug:slug>/submit/', views.work_submit, name='work_submit'),
]
