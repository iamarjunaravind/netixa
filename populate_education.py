import os
import django
import sys

# Setup Django environment
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'job_portal_core.settings')
django.setup()

from jobs.models import CourseCategory
from django.utils.text import slugify

def populate_categories():
    categories = {
        'Development': ['Python Full Stack', 'MERN Stack', 'MEAN Stack', 'Java Spring Boot', 'Data Science'],
        'Marketing': ['Digital Marketing', 'SEO Mastery', 'Social Media Marketing', 'Content Strategy'],
        'Trading': ['Stock Market Basics', 'Crypto Trading', 'Technical Analysis', 'Forex Trading'],
        'Designing': ['UI/UX Design', 'Graphic Design', 'Web Design', 'Adobe Illustrator'],
        'Yoga': ['Hatha Yoga', 'Meditation for Beginners', 'Kundalini Yoga', 'Power Yoga']
    }

    print("Populating Course Categories...")

    for parent_name, subcats in categories.items():
        # Create Parent Category
        parent_slug = slugify(parent_name)
        parent, created = CourseCategory.objects.get_or_create(
            slug=parent_slug,
            defaults={'name': parent_name, 'icon': 'fa-layer-group'}
        )
        if created:
            print(f"Created Parent: {parent_name}")
        else:
            print(f"Parent exists: {parent_name}")

        # Create Subcategories
        for sub_name in subcats:
            sub_slug = slugify(sub_name)
            sub, sub_created = CourseCategory.objects.get_or_create(
                slug=sub_slug,
                defaults={'name': sub_name, 'parent': parent, 'icon': 'fa-book'}
            )
            if sub_created:
                print(f"  - Created Sub: {sub_name}")
    
    print("Done!")

if __name__ == '__main__':
    populate_categories()
