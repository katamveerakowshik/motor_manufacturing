from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from .models import FreelancerProfile, WorkItem, Submission, CompanyStats
import json

User = get_user_model()

class UserRegistrationTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.register_url = reverse('freelancer:register')
    
    def test_user_registration(self):
        response = self.client.post(self.register_url, {
            'username': 'testuser',
            'email': 'test@example.com',
            'password1': 'testpassword123',
            'password2': 'testpassword123'
        })
        
        # Should redirect to successful registration page
        self.assertEqual(response.status_code, 302)
        
        # User should exist but not be active yet
        user = User.objects.get(username='testuser')
        self.assertFalse(user.is_active)
        self.assertFalse(user.is_approved)

class FreelancerEligibilityTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword123',
            is_active=True,
            is_approved=True
        )
        
        self.profile = FreelancerProfile.objects.get(user=self.user)
        self.client = Client()
        self.client.login(username='testuser', password='testpassword123')
        self.eligibility_url = reverse('freelancer:eligibility_form')
    
    def test_eligibility_validation(self):
        # Test with ineligible data (too young)
        today = timezone.now().date()
        response = self.client.post(self.eligibility_url, {
            'full_name': 'Test User',
            'date_of_birth': today - timedelta(days=17*365),
            'gender': 'M',
            'address': '123 Test St',
            'phone': '1234567890',
            'education': 'BACHELORS',
            'id_proof': 'ID12345',
            'certifications': ['ASE_CERTIFIED', 'AUTOMOTIVE_ENGINEERING']
        })
        
        # Should show form with errors
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "You must be at least 18 years old")
        
        # Test with eligible data
        response = self.client.post(self.eligibility_url, {
            'full_name': 'Test User',
            'date_of_birth': today - timedelta(days=25*365),
            'gender': 'M',
            'address': '123 Test St',
            'phone': '1234567890',
            'education': 'BACHELORS',
            'id_proof': 'ID12345',
            'certifications': ['ASE_CERTIFIED', 'AUTOMOTIVE_ENGINEERING']
        })
        
        # Should redirect to dashboard
        self.assertEqual(response.status_code, 302)
        
        # Refresh profile from database
        self.profile.refresh_from_db()
        self.assertTrue(self.profile.eligibility_completed)
        self.assertTrue(self.profile.is_eligible)

class WorkItemTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword123',
            is_active=True,
            is_approved=True
        )
        
        self.profile = FreelancerProfile.objects.get(user=self.user)
        self.profile.full_name = 'Test User'
        self.profile.date_of_birth = timezone.now().date() - timedelta(days=25*365)
        self.profile.gender = 'M'
        self.profile.education = 'BACHELORS'
        self.profile.certifications = json.dumps(['ASE_CERTIFIED'])
        self.profile.eligibility_completed = True
        self.profile.is_eligible = True
        self.profile.save()
        
        self.work_item = WorkItem.objects.create(
            title='Test Work Item',
            description='Test description',
            requirements='Test requirements',
            category='ENGINE'
        )
        
        self.client = Client()
        self.client.login(username='testuser', password='testpassword123')
        
    def test_work_item_assignment(self):
        assign_url = reverse('freelancer:work_select', args=[self.work_item.slug])
        
        response = self.client.post(assign_url)
        
        # Should redirect to work detail page
        self.assertEqual(response.status_code, 302)
        
        # Refresh work item from database
        self.work_item.refresh_from_db()
        self.assertEqual(self.work_item.status, 'ASSIGNED')
        self.assertEqual(self.work_item.assigned_to, self.user)
        
    def test_work_submission(self):
        # First assign the work item
        self.work_item.status = 'ASSIGNED'
        self.work_item.assigned_to = self.user
        self.work_item.assignment_time = timezone.now()
        self.work_item.save()
        
        submit_url = reverse('freelancer:work_submit', args=[self.work_item.slug])
        
        response = self.client.post(submit_url, {
            'notes': 'Completed as required',
            'components_used': 'Component A, Component B',
            'hours_spent': 10,
            'design_attachments': 'link1, link2',
            'quality_check_passed': True
        })
        
        # Should redirect to dashboard
        self.assertEqual(response.status_code, 302)
        
        # Check submission and work item status
        submission = Submission.objects.get(work_item=self.work_item, freelancer=self.user)
        self.assertEqual(submission.status, 'PENDING')
        
        self.work_item.refresh_from_db()
        self.assertEqual(self.work_item.status, 'COMPLETED')
