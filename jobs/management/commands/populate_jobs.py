from django.core.management.base import BaseCommand
from jobs.models import Job, Category, User, Company, Subscription
from django.utils import timezone
import random

class Command(BaseCommand):
    help = 'Populates the database with 100 dummy jobs across 10 categories'

    def handle(self, *args, **kwargs):
        self.stdout.write('Creating data...')

        # 1. Ensure Employer Exists
        employer_username = 'demo_employer'
        employer, created = User.objects.get_or_create(username=employer_username, defaults={
            'email': 'employer@demo.com',
            'first_name': 'Demo',
            'last_name': 'Employer',
            'user_type': 'employer',
            'is_verified': True
        })
        if created:
            employer.set_password('password123')
            employer.save()
            # Create Company
            Company.objects.create(
                user=employer,
                name='Tech Giants Inc.',
                description='A leading tech company.',
                location='San Francisco, CA'
            )
            # Subscription
            Subscription.objects.create(user=employer, plan_type='premium')
            self.stdout.write(f'Created employer: {employer_username}')
        else:
            self.stdout.write(f'Using existing employer: {employer_username}')

        # 2. Categories
        categories_list = [
            ('Software Development', 'fa-code'),
            ('Data Science', 'fa-database'),
            ('Design', 'fa-paint-brush'),
            ('Marketing', 'fa-bullhorn'),
            ('Sales', 'fa-chart-line'),
            ('Customer Support', 'fa-headset'),
            ('Finance', 'fa-money-bill-wave'),
            ('Human Resources', 'fa-users'),
            ('Product Management', 'fa-tasks'),
            ('Cyber Security', 'fa-shield-alt'),
        ]
        
        cats_objs = []
        for name, icon in categories_list:
            cat, _ = Category.objects.get_or_create(name=name, defaults={'icon': icon})
            cats_objs.append(cat)
        
        # 3. Jobs
        job_titles = [
            "Senior Developer", "Junior Analyst", "Manager", "Intern", "Director", 
            "Specialist", "Consultant", "Engineer", "Architect", "Lead"
        ]
        
        locations = ["New York", "Remote", "London", "Berlin", "San Francisco", "Austin", "Toronto", "Sydney", "Bangalore", "Dubai"]
        
        jobs_to_create = []
        for i in range(100):
            cat = random.choice(cats_objs)
            title = f"{random.choice(job_titles)} - {cat.name}"
            
            job = Job(
                employer=employer,
                company=employer.company,
                title=title,
                category=cat,
                description=f"This is a great opportunity for a {title}. Join us to make a difference.",
                location=random.choice(locations),
                job_type=random.choice(['full_time', 'part_time', 'contract', 'remote']),
                salary_range=f"${random.randint(50, 150)}k - ${random.randint(160, 250)}k",
                status='active',
                is_active=True,
                created_at=timezone.now()
            )
            jobs_to_create.append(job)
        
        Job.objects.bulk_create(jobs_to_create)
        self.stdout.write(self.style.SUCCESS('Successfully created 100 jobs'))
