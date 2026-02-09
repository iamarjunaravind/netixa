
import os
import django
import sys

# Set up Django environment
sys.path.append('c:/xampp/htdocs/job_portal')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'job_portal_core.settings')
django.setup()

from jobs.models import Job, User

def populate_data():
    print("Populating Job Slugs...")
    jobs = Job.objects.all()
    for job in jobs:
        if not job.slug:
            print(f"Updating slug for job: {job.title}")
            job.save() # save() method now handles slug generation

    print("Populating User Public IDs...")
    users = User.objects.all()
    for user in users:
        if not user.public_id:
            print(f"Updating public_id for user: {user.username}")
            user.save() # save() method now handles public_id generation

if __name__ == '__main__':
    populate_data()
    print("Done.")
