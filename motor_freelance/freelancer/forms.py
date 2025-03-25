from django import forms
from django.contrib.auth.forms import UserCreationForm, PasswordResetForm
from django.core.exceptions import ValidationError
from .models import User, FreelancerProfile, Submission

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("Email already exists")
        return email
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.is_active = False  # User will be activated after email verification
        user.is_approved = False
        if commit:
            user.save()
        return user

class FreelancerProfileForm(forms.ModelForm):
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other')
    ]
    
    EDUCATION_CHOICES = [
        ('HIGH_SCHOOL', 'High School'),
        ('DIPLOMA', 'Diploma'),
        ('BACHELORS', 'Bachelor\'s Degree'),
        ('MASTERS', 'Master\'s Degree'),
        ('PHD', 'PhD')
    ]
    
    CERTIFICATION_CHOICES = [
        ('ASE_CERTIFIED', 'ASE Certified'),
        ('MOTOR_TECH_INSTITUTE', 'Motor Technology Institute'),
        ('VEHICLE_DESIGN_SCHOOL', 'Vehicle Design School'),
        ('AUTOMOTIVE_ENGINEERING', 'Automotive Engineering Certificate'),
        ('INDUSTRIAL_DESIGN', 'Industrial Design Certificate')
    ]
    
    full_name = forms.CharField(max_length=100)
    date_of_birth = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    gender = forms.ChoiceField(choices=GENDER_CHOICES)
    address = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}))
    phone = forms.CharField(max_length=15)
    education = forms.ChoiceField(choices=EDUCATION_CHOICES)
    id_proof = forms.CharField(max_length=50, help_text="Enter your ID proof number (Passport/Driver's License/SSN)")
    certifications = forms.MultipleChoiceField(
        choices=CERTIFICATION_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        help_text="Select all certifications you have"
    )
    
    class Meta:
        model = FreelancerProfile
        fields = ['full_name', 'date_of_birth', 'gender', 'address', 'phone', 
                  'education', 'id_proof', 'certifications']
    
    def clean_date_of_birth(self):
        dob = self.cleaned_data.get('date_of_birth')
        from datetime import date
        today = date.today()
        age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
        
        if age < 18:
            raise ValidationError("You must be at least 18 years old to register.")
        elif age > 60:
            raise ValidationError("You must be under 60 years old to register.")
        
        return dob

class SubmissionForm(forms.ModelForm):
    notes = forms.CharField(widget=forms.Textarea)
    components_used = forms.CharField(widget=forms.Textarea, help_text="List all components used in the design")
    hours_spent = forms.IntegerField(min_value=1, help_text="Total hours spent on this work item")
    design_attachments = forms.CharField(widget=forms.Textarea, help_text="Provide links to your design files")
    quality_check_passed = forms.BooleanField(required=False)
    
    class Meta:
        model = Submission
        fields = ['notes', 'components_used', 'hours_spent', 'design_attachments', 'quality_check_passed']

class CustomPasswordResetForm(PasswordResetForm):
    def clean_email(self):
        email = self.cleaned_data['email']
        if not User.objects.filter(email=email).exists():
            raise ValidationError("There is no user registered with the specified email address.")
        return email
