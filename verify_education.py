import os
from django.db.models import Q
import django
import sys
from django.test import RequestFactory, Client
from django.urls import reverse

# Setup Django environment
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'job_portal_core.settings')
django.setup()

from jobs.models import User, Course, CourseCategory
from django.contrib.auth import get_user_model

User = get_user_model()

def verify_education_module():
    print("Starting Education Module Verification...")
    client = Client()
    
    # Check URLs
    urls_to_check = [
        ('jobs:learn', '/learn/'),
        ('jobs:college_signup', '/college/signup/'),
        ('jobs:college_dashboard', '/college/dashboard/'), # Protected
    ]
    
    print("\n[1/4] checking Route Configurations...")
    for name, path in urls_to_check:
        try:
            rev_path = reverse(name)
            if rev_path == path:
                 print(f"  OK: {name} -> {path}")
            else:
                 print(f"  WARN: {name} mapped to {rev_path}, expected {path}")
        except Exception as e:
            print(f"  FAIL: {name} - {e}")

    # Check Categories
    print("\n[2/4] Verifying Categories & Course Density...")
    parents = CourseCategory.objects.filter(parent__isnull=True)
    for p in parents:
        count = Course.objects.filter(Q(category=p) | Q(category__parent=p)).count()
        print(f"  - {p.name}: {count} courses")
        if count < 10:
            print(f"    WARN: {p.name} has less than 10 courses!")
    
    cats = CourseCategory.objects.count()
    print(f"  Total Categories: {cats}")

    # Check Views
    print("\n[3/4] Verifying Views...")
    
    # 3.1 Public Learn Page
    resp = client.get(reverse('jobs:learn'))
    if resp.status_code == 302: # Login required
        print("  OK: Learn View redirects to login (Authentication Protected)")
    elif resp.status_code == 200:
        print("  OK: Learn View accessible")
    else:
        print(f"  FAIL: Learn View returned {resp.status_code}")

    # 3.2 College Signup
    resp = client.get(reverse('jobs:college_signup'))
    if resp.status_code == 200:
        print("  OK: College Signup Page active")
    else:
        print(f"  FAIL: College Signup returned {resp.status_code}")

    print("\n[4/4] Module Integrity Check...")
    # Check if a college user exists or create one
    college_user, created = User.objects.get_or_create(username='test_college', defaults={'email': 'college@netixa.com', 'user_type': 'college'})
    if created:
        college_user.set_password('password123')
        college_user.save()
        print("  Created Mock College User.")
    
    # Check creating a course
    course_count_before = Course.objects.count()
    cat = CourseCategory.objects.first()
    course = Course.objects.create(
        title="Test Course Automation",
        college=college_user,
        category=cat,
        description="Test Description",
        duration="1 Hour",
        fees=10.00
    )
    print(f"  Created Mock Course: {course.slug}")
    
    if Course.objects.count() > course_count_before:
         print("  OK: Course creation logic functional.")
    else:
         print("  FAIL: Course was not created.")

    print("\nVerification Complete.")

if __name__ == '__main__':
    verify_education_module()
