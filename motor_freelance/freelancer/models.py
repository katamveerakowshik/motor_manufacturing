from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.utils.text import slugify
import uuid
import json

class User(AbstractUser):
    is_approved = models.BooleanField(default=False)
    
    def __str__(self):
        return self.username

class FreelancerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    full_name = models.CharField(max_length=100, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=1, choices=[('M', 'Male'), ('F', 'Female'), ('O', 'Other')], blank=True)
    address = models.TextField(blank=True)
    phone = models.CharField(max_length=15, blank=True)
    education = models.CharField(max_length=20, blank=True)
    id_proof = models.CharField(max_length=50, blank=True)
    certifications = models.TextField(blank=True, help_text="Store as JSON array")
    is_eligible = models.BooleanField(default=False)
    eligibility_completed = models.BooleanField(default=False)
    earnings = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username}'s profile"
    
    def get_certifications(self):
        if not self.certifications:
            return []
        return json.loads(self.certifications)
    
    def set_certifications(self, cert_list):
        self.certifications = json.dumps(cert_list)
    
    def check_eligibility(self):
        """Check if the freelancer meets all eligibility criteria"""
        if not self.date_of_birth:
            return False
        
        # Age check (18-60)
        from datetime import date
        today = date.today()
        age = today.year - self.date_of_birth.year - ((today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day))
        if age < 18 or age > 60:
            return False
        
        # Education check (minimum graduation)
        eligible_education = ['BACHELORS', 'MASTERS', 'PHD']
        if self.education not in eligible_education:
            return False
        
        # Certification check (at least one certification)
        if not self.certifications or len(self.get_certifications()) == 0:
            return False
        
        return True
    
    def save(self, *args, **kwargs):
        if self.eligibility_completed:
            self.is_eligible = self.check_eligibility()
        super().save(*args, **kwargs)

class CompanyStats(models.Model):
    date = models.DateField(default=timezone.now)
    vehicles_sold = models.IntegerField(default=0)
    total_revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    production_rate = models.IntegerField(default=0)
    customer_satisfaction = models.DecimalField(max_digits=3, decimal_places=1, default=0)
    
    class Meta:
        verbose_name_plural = "Company Stats"
        ordering = ['-date']
    
    def __str__(self):
        return f"Stats for {self.date}"

class WorkItem(models.Model):
    STATUS_CHOICES = [
        ('AVAILABLE', 'Available'),
        ('ASSIGNED', 'Assigned'),
        ('COMPLETED', 'Completed'),
        ('REVIEWED', 'Reviewed')
    ]
    
    CATEGORY_CHOICES = [
        ('ENGINE', 'Engine Design'),
        ('CHASSIS', 'Chassis Design'),
        ('INTERIOR', 'Interior Design'),
        ('ELECTRICAL', 'Electrical Systems'),
        ('BODY', 'Body Design'),
        ('TESTING', 'Testing & Validation')
    ]
    
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=250, unique=True, blank=True)
    description = models.TextField()
    requirements = models.TextField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='AVAILABLE')
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_works')
    assignment_time = models.DateTimeField(null=True, blank=True)
    expected_hours = models.IntegerField(default=8)
    priority = models.IntegerField(default=1)  # 1=low, 2=medium, 3=high
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    lock_version = models.IntegerField(default=0)  # For optimistic locking
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
            # Ensure uniqueness
            original_slug = self.slug
            counter = 1
            while WorkItem.objects.filter(slug=self.slug).exists():
                self.slug = f"{original_slug}-{counter}"
                counter += 1
        super().save(*args, **kwargs)

class Submission(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending Review'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected')
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    work_item = models.ForeignKey(WorkItem, on_delete=models.CASCADE, related_name='submissions')
    freelancer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='submissions')
    notes = models.TextField()
    components_used = models.TextField(blank=True)
    hours_spent = models.IntegerField(default=0)
    design_attachments = models.TextField(blank=True)
    quality_check_passed = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    reviewer_comments = models.TextField(blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-submitted_at']
    
    def __str__(self):
        return f"Submission for {self.work_item.title} by {self.freelancer.username}"
    
    def approve(self, reviewer_comments=''):
        """Approve the submission and update related records"""
        from django.db import transaction
        
        with transaction.atomic():
            self.status = 'APPROVED'
            self.reviewer_comments = reviewer_comments
            self.reviewed_at = timezone.now()
            self.save()
            
            # Update work item status
            self.work_item.status = 'REVIEWED'
            self.work_item.save()
            
            # Update freelancer earnings (1000rs per successful submission)
            profile = self.freelancer.profile
            print(f"Before update: {profile.user.username} earnings = {profile.earnings}")
            profile.earnings = profile.earnings + 1000  # Explicit calculation to avoid issues
            print(f"After update: {profile.user.username} earnings = {profile.earnings}")
            profile.save(update_fields=['earnings'])  # Ensure only earnings is updated
    
    def reject(self, reviewer_comments):
        """Reject the submission and update related records"""
        self.status = 'REJECTED'
        self.reviewer_comments = reviewer_comments
        self.reviewed_at = timezone.now()
        self.save()
        
        # Make the work item available again
        self.work_item.status = 'AVAILABLE'
        self.work_item.assigned_to = None
        self.work_item.assignment_time = None
        self.work_item.save()
