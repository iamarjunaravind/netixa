import os
import django
import sys
from django.urls import reverse
from django.test import RequestFactory
from django.contrib.auth import get_user_model

# Setup Django
sys.path.append('c:/xampp/htdocs/job_portal')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'job_portal_core.settings')
django.setup()

from jobs.models import Job, Company, Application
from jobs import views

def run_checks():
    print("Starting Full Site Verification...")
    User = get_user_model()
    factory = RequestFactory()
    
    # 1. Verify URL Reversing for new pages
    print("\n[1/4] Verifying URL Configuration...")
    try:
        pages = [
            'jobs:network', 
            'jobs:messaging', 
            'jobs:notifications', 
            'jobs:profile', 
            'jobs:employer_dashboard',
            'jobs:applicant_dashboard'
        ]
        all_passed = True
        for page in pages:
            try:
                url = reverse(page)
                print(f"  OK: {page} -> {url}")
            except Exception as e:
                print(f"  FAIL: Could not reverse {page}: {e}")
                all_passed = False
        if all_passed:
            print("  SUCCESS: All core URLs verified.")
    except Exception as e:
        print(f"  FAIL: Verification of URLs failed: {e}")
        return

    # 2. Verify View Logic (Basic Instantiation)
    print("\n[2/4] Verifying View Accessibility (Mock Request)...")
    # Create valid user
    user, _ = User.objects.get_or_create(username='verify_user', defaults={'email': 'verify@test.com', 'user_type': 'applicant'})
    
    view_tests = [
        ('HomeView', views.HomeView.as_view(), 'jobs:home'),
        ('MessagingView', views.MessagingView.as_view(), 'jobs:messaging'),
        ('NetworkView', views.NetworkView.as_view(), 'jobs:network'),
        ('NotificationsView', views.NotificationsView.as_view(), 'jobs:notifications'),
        ('LearnView', views.LearnView.as_view(), 'jobs:learn'),
        ('ProfileView', views.ProfileView.as_view(), 'jobs:profile'),
    ]

    for name, view, url_name in view_tests:
        try:
            request = factory.get(reverse(url_name))
            request.user = user
            response = view(request)
            if response.status_code == 200:
                print(f"  OK: {name} returned 200")
            else:
                print(f"  FAIL: {name} returned {response.status_code}")
        except Exception as e:
             print(f"  FAIL: {name} raised error: {e}")


    # 3. Verify Job Creation Flow (Model level)
    print("\n[3/4] Verifying Job Creation Flow...")
    try:
        emp_user, _ = User.objects.get_or_create(username='verify_emp', defaults={'email': 'emp@test.com', 'user_type': 'employer'})
        company, _ = Company.objects.get_or_create(user=emp_user, defaults={'name': 'Verify Corp'})
        
        # Create a unique slug to avoid conflict in repeated runs
        import random
        slug_suffix = random.randint(1000, 9999)
        job_slug = f'verify-job-{slug_suffix}'
        
        job = Job.objects.create(
            employer=emp_user, 
            company=company, 
            title='Verify Job', 
            slug=job_slug,
            description="Test description",
            job_type='full_time',
            location='Remote'
        )
        print(f"  OK: Job '{job.title}' created with slug '{job.slug}'")
    except Exception as e:
        print(f"  FAIL: Job creation failed: {e}")

    # 4. Verify Template Rendering (Direct Check)
    print("\n[4/4] Verifying Template Existence...")
    from django.template.loader import get_template
    templates = [
        'jobs/home.html',
        'jobs/network.html',
        'jobs/messaging.html',
        'jobs/notifications.html',
        'jobs/learn.html',
        'jobs/profile.html',
        'jobs/profile_edit.html'
    ]
    for tmpl in templates:
        try:
            get_template(tmpl)
            print(f"  OK: Template found: {tmpl}")
        except Exception as e:
            print(f"  FAIL: Template missing: {tmpl} ({e})")

    print("\nVerification Script Complete.")

if __name__ == '__main__':
    run_checks()
