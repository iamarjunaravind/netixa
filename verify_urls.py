
import os
import django
import sys
from django.urls import reverse

# Set up Django environment
sys.path.append('c:/xampp/htdocs/job_portal')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'job_portal_core.settings')
django.setup()

from jobs.models import Job, User

def verify_urls():
    print("Verifying Job URLs...")
    jobs = Job.objects.all()[:5]
    for job in jobs:
        if not job.slug:
            print(f"ERROR: Job {job.title} has no slug!")
            continue
        try:
            url = reverse('jobs:job_detail', kwargs={'slug': job.slug})
            print(f"SUCCESS: Job '{job.title}' -> {url}")
        except Exception as e:
            print(f"ERROR: Could not reverse URL for job '{job.title}': {e}")

    print("\nVerifying User URLs...")
    users = User.objects.all()[:5]
    for user in users:
        if not user.public_id:
            print(f"ERROR: User {user.username} has no public_id!")
            continue
        try:
            # Check verify_user URL as an example of user URL usage
            url = reverse('jobs:verify_user', kwargs={'public_id': user.public_id})
            print(f"SUCCESS: User '{user.username}' -> {url}")
        except Exception as e:
            print(f"ERROR: Could not reverse URL for user '{user.username}': {e}")

if __name__ == '__main__':
    verify_urls()
