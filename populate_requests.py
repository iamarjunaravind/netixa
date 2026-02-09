import os
import django
import sys

# Setup Django environment
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'job_portal_core.settings')
django.setup()

from jobs.models import User, Connection

def populate_requests():
    # Ensure we have users
    users = User.objects.filter(user_type='applicant')
    if users.count() < 2:
        print("Not enough users to create connections.")
        return

    # Assuming we are logged in as 'student1' (or the first user), let's create requests FOR them from others
    current_user = users.first() # Or specific one like User.objects.get(username='student1')
    others = users.exclude(id=current_user.id)

    print(f"Creating requests for {current_user.username}...")

    count = 0
    for other in others[:3]: # Create 3 requests
        # Check existing
        if not Connection.objects.filter(sender=other, recipient=current_user).exists():
            Connection.objects.create(sender=other, recipient=current_user, status='pending')
            print(f"Request from {other.username} created.")
            count += 1
    
    # Also create connections where current user is sender (to verify they don't show up in suggestions)
    for other in others[3:5]:
         if not Connection.objects.filter(sender=current_user, recipient=other).exists():
            Connection.objects.create(sender=current_user, recipient=other, status='pending')
            print(f"Request to {other.username} sent.")

    print(f"Done. Created {count} incoming requests.")

if __name__ == "__main__":
    populate_requests()
