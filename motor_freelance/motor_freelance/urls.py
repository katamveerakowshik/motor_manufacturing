"""
URL configuration for motor_freelance project.
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('freelancer.urls')),
]
