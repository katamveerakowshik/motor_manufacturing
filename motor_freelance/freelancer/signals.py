from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User, FreelancerProfile, WorkItem
from django.utils import timezone
import random

@receiver(post_save, sender=User)
def create_freelancer_profile(sender, instance, created, **kwargs):
    """Create a FreelancerProfile when a new User is created"""
    if created:
        FreelancerProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_freelancer_profile(sender, instance, **kwargs):
    """Save the FreelancerProfile when the User is saved"""
    if hasattr(instance, 'profile'):
        instance.profile.save()

@receiver(post_save, sender=FreelancerProfile)
def generate_sample_work_items(sender, instance, created, **kwargs):
    """Generate sample work items if none exist (for demo purposes)"""
    if WorkItem.objects.count() == 0:
        # Sample work item data
        work_items = [
            {
                'title': 'Engine Design Optimization for 1.5L Turbo',
                'description': 'Optimize the engine design for our upcoming 1.5L Turbocharged engine to improve fuel efficiency by 10% while maintaining or improving power output.',
                'requirements': 'Experience with engine thermodynamics, CAD software, and optimization algorithms. Knowledge of turbocharger systems required.',
                'category': 'ENGINE',
                'expected_hours': 40,
                'priority': 3
            },
            {
                'title': 'Interior Dashboard Layout for SUV Model',
                'description': 'Design a modern, ergonomic dashboard layout for our new SUV model with integrated touchscreen and climate controls.',
                'requirements': 'Experience with interior design, ergonomics, and human-machine interface design. Knowledge of automotive safety standards required.',
                'category': 'INTERIOR',
                'expected_hours': 30,
                'priority': 2
            },
            {
                'title': 'Aerodynamic Body Design for Sports Model',
                'description': 'Create an aerodynamic body design for our upcoming sports car model to reduce drag coefficient while maintaining aesthetic appeal.',
                'requirements': 'Experience with aerodynamics, CFD analysis, and automotive styling. Portfolio of previous automotive design work required.',
                'category': 'BODY',
                'expected_hours': 50,
                'priority': 2
            },
            {
                'title': 'Electric Wiring Diagram for Hybrid System',
                'description': 'Develop comprehensive wiring diagrams for our new hybrid powertrain system including battery management, motor controls, and integration with existing systems.',
                'requirements': 'Experience with automotive electrical systems, hybrid/electric vehicles, and wiring diagram creation. Knowledge of automotive safety standards required.',
                'category': 'ELECTRICAL',
                'expected_hours': 35,
                'priority': 3
            },
            {
                'title': 'Chassis Reinforcement Design for Safety',
                'description': 'Design reinforcement structures for our compact car chassis to improve crash test ratings while minimizing weight increase.',
                'requirements': 'Experience with structural engineering, finite element analysis, and lightweight materials. Knowledge of automotive safety standards required.',
                'category': 'CHASSIS',
                'expected_hours': 25,
                'priority': 1
            },
            {
                'title': 'Sound Insulation Design for Luxury Sedan',
                'description': 'Develop a comprehensive sound insulation strategy for our luxury sedan to reduce interior noise levels by at least 3dB across all frequencies.',
                'requirements': 'Experience with acoustic engineering, materials science, and NVH testing. Previous experience with luxury vehicles preferred.',
                'category': 'INTERIOR',
                'expected_hours': 20,
                'priority': 1
            },
            {
                'title': 'Cooling System Optimization for Performance Engine',
                'description': 'Optimize the cooling system for our high-performance 3.0L engine to prevent overheating during extended high-speed operation while minimizing weight and packaging space.',
                'requirements': 'Experience with thermal management systems, fluid dynamics, and high-performance engines. Knowledge of radiator and pump design required.',
                'category': 'ENGINE',
                'expected_hours': 30,
                'priority': 2
            },
        ]
        
        # Create work items
        for item in work_items:
            WorkItem.objects.create(
                title=item['title'],
                description=item['description'],
                requirements=item['requirements'],
                category=item['category'],
                expected_hours=item['expected_hours'],
                priority=item['priority'],
                created_at=timezone.now() - timezone.timedelta(days=random.randint(1, 10))
            )
