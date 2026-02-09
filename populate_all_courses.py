import os
import django
import sys
from django.utils.text import slugify
import random

# Setup Django environment
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'job_portal_core.settings')
django.setup()

from jobs.models import User, Course, CourseCategory

def populate_all_courses():
    print("Starting course population for all categories...")
    
    # Ensure we have a college user
    college_user, created = User.objects.get_or_create(
        username='netixa_college',
        defaults={
            'email': 'edu@netixa.com',
            'user_type': 'college',
            'is_active': True
        }
    )
    if created:
        college_user.set_password('password123')
        college_user.save()
        print(f"  Created College User: {college_user.username}")

    # Titles for subcategories to make it look realistic
    course_variations = [
        "Masterclass 2026", "Complete Bootcamp", "The Ultimate Guide", 
        "Advanced Techniques", "Essentials Training", "Industry Secrets",
        "for Professionals", "Crash Course", "Zero to Hero", "Hands-on Workshop"
    ]

    subcategories = CourseCategory.objects.filter(parent__isnull=False)
    print(f"  Found {subcategories.count()} subcategories.")

    courses_created = 0
    for subcat in subcategories:
        # Create 3-4 courses for each subcategory to ensure main categories (parents) have > 10
        num_to_create = random.randint(3, 4)
        for i in range(num_to_create):
            variation = random.choice(course_variations)
            title = f"{subcat.name} {variation}"
            slug = slugify(f"{subcat.slug}-{variation}-{random.randint(100, 999)}")
            
            course, created = Course.objects.get_or_create(
                slug=slug,
                defaults={
                    'title': title,
                    'college': college_user,
                    'category': subcat,
                    'description': f"Become an expert in {subcat.name}. This course covers everything from {variation} to advanced practical implementation. Join thousands of students already learning {subcat.name} with Netixa.",
                    'duration': f"{random.randint(2, 16)} {random.choice(['Weeks', 'Hours', 'Sessions'])}",
                    'fees': random.choice([0.00, 9.99, 14.99, 29.99, 49.99, 79.00, 149.00]),
                    'level': random.choice(['beginner', 'intermediate', 'advanced']),
                    'rating': random.uniform(4.0, 5.0),
                    'students_enrolled': random.randint(100, 5000)
                }
            )
            if created:
                courses_created += 1
                if courses_created % 10 == 0:
                    print(f"    - Created {courses_created} courses so far...")

    print(f"\nPopulation complete. Total new courses created: {courses_created}")

if __name__ == '__main__':
    populate_all_courses()
