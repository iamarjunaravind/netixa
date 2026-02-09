import os
import django
import sys

# Setup Django environment
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'job_portal_core.settings')
django.setup()

from jobs.models import Course, CourseModule, Lesson

def populate_curriculum():
    courses = Course.objects.all()
    if not courses.exists():
        print("No courses found. Please run populate_education.py or create courses first.")
        return

    print(f"Populating curriculum for {courses.count()} courses...")

    for course in courses:
        # Create 3 modules for each course
        for i in range(1, 4):
            module, created = CourseModule.objects.get_or_create(
                course=course,
                title=f"Module {i}: Foundations of {course.title}",
                defaults={'order': i}
            )
            if created:
                print(f"  Created Module: {module.title}")
            
            # Create 2 lessons for each module
            for j in range(1, 3):
                lesson_title = f"Lesson {j}: Understanding the Basics of {course.title}"
                lesson, l_created = Lesson.objects.get_or_create(
                    module=module,
                    title=lesson_title,
                    defaults={
                        'description': f"This lesson covers the core concepts of {course.title} within {module.title}.",
                        'video_url': 'https://www.youtube.com/embed/dQw4w9WgXcQ', # Dummy video
                        'duration': '15 mins',
                        'order': j
                    }
                )
                if l_created:
                    print(f"    - Created Lesson: {lesson.title}")

    print("Done!")

if __name__ == '__main__':
    populate_curriculum()
