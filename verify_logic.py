from django.contrib.auth import get_user_model
from jobs.models import Job, Company, SavedJob, HiddenJob, Category

User = get_user_model()

# Setup
user, _ = User.objects.get_or_create(username='test_verify', email='test@example.com', defaults={'user_type': 'applicant'})
employer, _ = User.objects.get_or_create(username='test_employer', email='emp@example.com', defaults={'user_type': 'employer'})
company, _ = Company.objects.get_or_create(user=employer, defaults={'name': 'Test Corp', 'description': 'desc', 'location': 'Loc'})
category, _ = Category.objects.get_or_create(name='IT')
job, _ = Job.objects.get_or_create(employer=employer, company=company, title='Test Job', description='Desc', location='Loc', job_type='full_time', category=category)

# Test Save
print("Testing Save...")
SavedJob.objects.create(user=user, job=job)
assert SavedJob.objects.filter(user=user, job=job).exists()
print("Save OK")

# Test Hide
print("Testing Hide...")
HiddenJob.objects.create(user=user, job=job)
assert HiddenJob.objects.filter(user=user, job=job).exists()
print("Hide OK")

# Test Exclude Hidden
print("Testing Queryset Exclude...")
# Mimic JobListView logic
queryset = Job.objects.all().exclude(hidden_by_users__user=user)
assert not queryset.filter(id=job.id).exists()
print("Exclude OK")

print("Verification Script Completed Successfully.")
