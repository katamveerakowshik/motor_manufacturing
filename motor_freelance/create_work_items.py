from freelancer.models import WorkItem
from django.utils.text import slugify
import random

# Sample work items
titles = [
    'Engine Block Redesign', 
    'Fuel System Optimization', 
    'Exhaust Manifold Update', 
    'Transmission Housing Design', 
    'Cooling System Improvement'
]

categories = ['ENGINE', 'CHASSIS', 'INTERIOR', 'ELECTRICAL', 'BODY', 'TESTING']

# Create work items
for title in titles:
    WorkItem.objects.create(
        title=title, 
        slug=slugify(title), 
        description=f'Design a new {title.lower()} for our latest vehicle model.',
        requirements=f'Must meet industry standards for {title.lower()}.',
        category=random.choice(categories),
        expected_hours=random.randint(4, 20),
        priority=random.randint(1, 3)
    )

print(f"Created {len(titles)} work items successfully!")