from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.urls import reverse
from django.db import transaction, IntegrityError
from django.http import HttpResponseRedirect
from django.contrib.auth.views import PasswordResetView
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import EmailMessage
from django.conf import settings

from .models import User, FreelancerProfile, WorkItem, Submission, CompanyStats
from .forms import UserRegistrationForm, FreelancerProfileForm, SubmissionForm, CustomPasswordResetForm
from .tokens import account_activation_token

import random
import json

def home(request):
    """Landing page"""
    return render(request, 'freelancer/home.html', {'title': 'Welcome to Motor Manufacturing Freelancer Portal'})

def register(request):
    """User registration view"""
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            # Send account activation email
            current_site = get_current_site(request)
            mail_subject = 'Activate your Motor Manufacturing account'
            message = render_to_string('freelancer/email/activation_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': account_activation_token.make_token(user),
                'protocol': 'https' if request.is_secure() else 'http'
            })
            to_email = form.cleaned_data.get('email')
            email = EmailMessage(mail_subject, message, to=[to_email])
            email.send()
            
            messages.success(request, 'Your account has been created! Please check your email to activate your account.')
            return redirect('freelancer:login')
    else:
        form = UserRegistrationForm()
    return render(request, 'freelancer/register.html', {'form': form, 'title': 'Register'})

def activate_account(request, uidb64, token):
    """Activate user account after email verification"""
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.is_approved = True
        user.save()
        
        # Create profile for user if it doesn't exist
        FreelancerProfile.objects.get_or_create(user=user)
        
        messages.success(request, 'Your account has been activated! You can now log in.')
        return redirect('freelancer:login')
    else:
        messages.error(request, 'Activation link is invalid or has expired!')
        return redirect('freelancer:home')

def user_login(request):
    """User login view"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            if user.is_active and user.is_approved:
                login(request, user)
                
                # Redirect to eligibility form if not completed, otherwise dashboard
                if hasattr(user, 'profile') and not user.profile.eligibility_completed:
                    return redirect('freelancer:eligibility_form')
                return redirect('freelancer:dashboard')
            else:
                messages.error(request, 'Your account is not active or approved yet.')
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'freelancer/login.html', {'title': 'Login'})

def user_logout(request):
    """User logout view"""
    logout(request)
    messages.success(request, 'You have been successfully logged out.')
    return redirect('freelancer:login')

class CustomPasswordResetView(PasswordResetView):
    template_name = 'freelancer/password_reset.html'
    form_class = CustomPasswordResetForm
    email_template_name = 'freelancer/email/reset_password_email.html'
    success_url = '/password-reset/done/'

custom_password_reset = CustomPasswordResetView.as_view()

@login_required
def dashboard(request):
    """User dashboard with performance stats and work items"""
    # Get company stats
    try:
        latest_stats = CompanyStats.objects.latest('date')
    except CompanyStats.DoesNotExist:
        # Create some sample stats if none exist
        latest_stats = generate_company_stats()
    
    # Get user's work items
    user_works = WorkItem.objects.filter(assigned_to=request.user)
    
    # Get available work items
    available_works = []
    if hasattr(request.user, 'profile') and request.user.profile.is_eligible:
        available_works = WorkItem.objects.filter(status='AVAILABLE')[:5]
    
    # Get user's pending and completed submissions
    pending_submissions = Submission.objects.filter(
        freelancer=request.user, 
        status='PENDING'
    ).select_related('work_item')
    
    completed_submissions = Submission.objects.filter(
        freelancer=request.user, 
        status='APPROVED'
    ).select_related('work_item')[:5]
    
    context = {
        'title': 'Dashboard',
        'stats': latest_stats,
        'user_works': user_works,
        'available_works': available_works,
        'pending_submissions': pending_submissions,
        'completed_submissions': completed_submissions,
        'profile': request.user.profile if hasattr(request.user, 'profile') else None
    }
    
    return render(request, 'freelancer/dashboard.html', context)

@login_required
def profile(request):
    """User profile view"""
    profile = get_object_or_404(FreelancerProfile, user=request.user)
    
    context = {
        'title': 'My Profile',
        'profile': profile
    }
    
    return render(request, 'freelancer/profile.html', context)

@login_required
def eligibility_form(request):
    """Eligibility criteria form for first-time users"""
    profile = get_object_or_404(FreelancerProfile, user=request.user)
    
    # Redirect to dashboard if already completed eligibility
    if profile.eligibility_completed:
        return redirect('freelancer:dashboard')
    
    if request.method == 'POST':
        form = FreelancerProfileForm(request.POST, instance=profile)
        if form.is_valid():
            # Save profile data
            profile = form.save(commit=False)
            
            # Save certifications as JSON
            certifications = request.POST.getlist('certifications')
            profile.set_certifications(certifications)
            
            profile.eligibility_completed = True
            profile.save()
            
            if profile.is_eligible:
                messages.success(request, 'Congratulations! You meet our eligibility criteria and can now access work items.')
            else:
                messages.error(request, 'Unfortunately, you do not meet our eligibility criteria at this time.')
            
            return redirect('freelancer:dashboard')
    else:
        form = FreelancerProfileForm(instance=profile)
    
    context = {
        'title': 'Eligibility Form',
        'form': form
    }
    
    return render(request, 'freelancer/eligibility_form.html', context)

@login_required
def work_list(request):
    """List all available work items"""
    profile = get_object_or_404(FreelancerProfile, user=request.user)
    
    # Check if user is eligible
    if not profile.is_eligible:
        messages.error(request, 'You are not eligible to view work items.')
        return redirect('freelancer:dashboard')
    
    # Get all available work items
    works = WorkItem.objects.filter(status='AVAILABLE')
    
    # Get user's assigned works
    user_works = WorkItem.objects.filter(assigned_to=request.user)
    
    context = {
        'title': 'Available Work',
        'works': works,
        'user_works': user_works,
    }
    
    return render(request, 'freelancer/work_list.html', context)

@login_required
def work_detail(request, slug):
    """Show details of a specific work item"""
    profile = get_object_or_404(FreelancerProfile, user=request.user)
    
    # Check if user is eligible
    if not profile.is_eligible:
        messages.error(request, 'You are not eligible to view work items.')
        return redirect('freelancer:dashboard')
    
    work_item = get_object_or_404(WorkItem, slug=slug)
    
    # Check if work item is assigned to current user or is available
    if work_item.status != 'AVAILABLE' and work_item.assigned_to != request.user:
        messages.error(request, 'This work item is not available or assigned to you.')
        return redirect('freelancer:work_list')
    
    # Create submission form if the work is assigned to the current user
    form = None
    if work_item.status == 'ASSIGNED' and work_item.assigned_to == request.user:
        form = SubmissionForm()
    
    context = {
        'title': work_item.title,
        'work': work_item,
        'is_assigned': work_item.assigned_to == request.user,
        'form': form,
        'profile': profile
    }
    
    return render(request, 'freelancer/work_detail.html', context)

@login_required
def work_select(request, slug):
    """Assign a work item to the current user with concurrency control"""
    profile = get_object_or_404(FreelancerProfile, user=request.user)
    
    # Check if user is eligible
    if not profile.is_eligible:
        messages.error(request, 'You are not eligible to select work items.')
        return redirect('freelancer:dashboard')
    
    if request.method == 'POST':
        with transaction.atomic():
            # Lock the row for update
            work_item = get_object_or_404(WorkItem.objects.select_for_update(), slug=slug)
            
            # Check if work is available
            if work_item.status != 'AVAILABLE':
                messages.error(request, 'This work item is no longer available.')
                return redirect('freelancer:work_list')
            
            # Assign work to current user
            work_item.status = 'ASSIGNED'
            work_item.assigned_to = request.user
            work_item.assignment_time = timezone.now()
            work_item.lock_version += 1
            work_item.save()
            
            messages.success(request, f'You have successfully selected "{work_item.title}"')
            return redirect('freelancer:work_detail', slug=work_item.slug)
    
    return redirect('freelancer:work_detail', slug=slug)

@login_required
def work_submit(request, slug):
    """Submit completed work"""
    work_item = get_object_or_404(WorkItem, slug=slug, assigned_to=request.user)
    
    if work_item.status != 'ASSIGNED':
        messages.error(request, 'This work item cannot be submitted.')
        return redirect('freelancer:dashboard')
    
    if request.method == 'POST':
        form = SubmissionForm(request.POST)
        if form.is_valid():
            submission = form.save(commit=False)
            submission.work_item = work_item
            submission.freelancer = request.user
            submission.save()
            
            # Update work item status
            work_item.status = 'COMPLETED'
            work_item.save()
            
            messages.success(request, 'Your work has been submitted successfully and is pending review. Once approved by admin, 1000rs will be added to your earnings.')
            
            return redirect('freelancer:dashboard')
    else:
        form = SubmissionForm()
    
    context = {
        'title': f'Submit Work: {work_item.title}',
        'work': work_item,
        'form': form
    }
    
    return render(request, 'freelancer/work_detail.html', context)

def generate_company_stats():
    """Generate sample company stats for demo purposes"""
    today = timezone.now().date()
    
    # Check if stats for today already exist
    if CompanyStats.objects.filter(date=today).exists():
        return CompanyStats.objects.get(date=today)
    
    # Create new stats
    vehicles_sold = random.randint(50, 200)
    revenue = vehicles_sold * random.randint(500000, 2000000)
    production_rate = random.randint(40, 180)
    satisfaction = round(random.uniform(3.5, 4.9), 1)
    
    stats = CompanyStats.objects.create(
        date=today,
        vehicles_sold=vehicles_sold,
        total_revenue=revenue,
        production_rate=production_rate,
        customer_satisfaction=satisfaction
    )
    
    return stats
