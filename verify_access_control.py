import os
import django
import sys
from django.test import Client
from django.urls import reverse
from django.test.utils import setup_test_environment

# Setup Django environment
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'job_portal_core.settings')
django.setup()
setup_test_environment()

from jobs.models import Job, User, Company, Article, Course

def verify_access():
    client = Client()
    print("Verifying Access Control...")

    # 1. Check Public Access (Should be 200 OK)
    public_urls = [
        ('jobs:job_list', {}, '/jobs/'),
        ('jobs:network', {}, '/network/'),
        ('jobs:learn', {}, '/learn/'),
        ('jobs:article_list', {}, '/articles/'),
    ]

    print("[1] Verifying Public Lists (Should be 200 OK)...")
    for name, kwargs, path in public_urls:
        try:
            url = reverse(name, kwargs=kwargs)
            resp = client.get(url)
            if resp.status_code == 200:
                print(f"  OK: {url} accessible (Public).")
            else:
                print(f"  FAIL: {url} returned {resp.status_code} (expected 200)")
        except Exception as e:
            print(f"  ERROR checking {name}: {e}")

    # 2. Check Private Access (Should Redirect)
    print("\n[2] Verifying Private Details (Should Redirect to Login)...")
    
    job = Job.objects.first()
    course = Course.objects.first()
    article = Article.objects.first()

    private_urls = []
    if job: private_urls.append(('jobs:job_detail', {'slug': job.slug}, f'/job/{job.slug}/'))
    if course: private_urls.append(('jobs:course_detail', {'slug': course.slug}, f'/learn/{course.slug}/'))
    if article: private_urls.append(('jobs:article_detail', {'slug': article.slug}, f'/article/{article.slug}/'))

    for name, kwargs, path in private_urls:
         try:
            url = reverse(name, kwargs=kwargs)
            resp = client.get(url)
            if resp.status_code == 302 and '/login/' in resp.url:
                print(f"  OK: {url} redirected to login.")
            else:
                print(f"  FAIL: {url} returned {resp.status_code} (expected 302)")
         except Exception as e:
            print(f"  ERROR checking {name}: {e}")

    # 3. Check Data Counts
    print("\n[3] Verifying Data Counts...")
    print(f"  Jobs: {Job.objects.count()}")
    print(f"  Courses: {Course.objects.count()}")
    print(f"  Articles: {Article.objects.count()}")
    print(f"  Users: {User.objects.count()}")

if __name__ == '__main__':
    verify_access()
