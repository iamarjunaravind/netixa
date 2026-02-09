import os
import django
import random
import requests
from django.core.files import File
from django.utils.text import slugify

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'job_portal_core.settings')
django.setup()

from jobs.models import Course, CourseCategory

def populate_course_images():
    print("Populating Course Images...")

    # Mapping Categories to Keywords
    CATEGORY_KEYWORDS = {
        'Development': ['coding', 'programmer', 'laptop', 'software'],
        'Marketing': ['digital marketing', 'social media', 'analytics'],
        'Trading': ['stock market', 'trading chart', 'finance'],
        'Designing': ['graphic design', 'ui ux', 'creative'],
        'Yoga': ['yoga', 'meditation', 'fitness'],
        # Fallbacks
        'Business': ['meeting', 'office'],
    }

    media_root = 'media/course_images_pool'
    os.makedirs(media_root, exist_ok=True)

    def download_image(keyword, index):
        url = f"https://loremflickr.com/800/600/{keyword.replace(' ', ',')}?lock={index}"
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                safe_keyword = keyword.replace(' ', '_')
                filename = f"{safe_keyword}_{index}.jpg"
                path = os.path.join(media_root, filename)
                with open(path, 'wb') as f:
                    f.write(response.content)
                return path
        except Exception as e:
            print(f"Error downloading {keyword}: {e}")
        return None

    # Get all courses
    courses = Course.objects.all()
    count = 0

    for course in courses:
        # Determine keyword
        cat_name = course.category.name if course.category else 'Business'
        keywords = CATEGORY_KEYWORDS.get(cat_name)
        
        # If no direct match, check parent
        if not keywords and course.category and course.category.parent:
             keywords = CATEGORY_KEYWORDS.get(course.category.parent.name)
        
        if not keywords:
            keywords = ['education', 'learning']

        keyword = random.choice(keywords)
        
        # Unique locking to get different images
        img_path = download_image(keyword, course.id) 
        
        if img_path:
            with open(img_path, 'rb') as f:
                filename = os.path.basename(img_path)
                course.image.save(filename, File(f), save=True)
                count += 1
                print(f"Updated {course.title} with image for '{keyword}'")

    print(f"Done! Updated {count} courses.")

if __name__ == '__main__':
    populate_course_images()
