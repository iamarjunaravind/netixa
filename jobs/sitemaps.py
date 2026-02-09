from django.contrib.sitemaps import Sitemap
from .models import Job, Course

class JobSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.8

    def items(self):
        # Only index active jobs
        return Job.objects.filter(status='active').order_by('-created_at')

    def lastmod(self, obj):
        return obj.updated_at

class CourseSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.7

    def items(self):
        return Course.objects.all().order_by('-created_at')

    def lastmod(self, obj):
        return obj.updated_at

class StaticViewSitemap(Sitemap):
    priority = 0.5
    changefreq = 'monthly'

    def items(self):
        return ['jobs:home', 'jobs:job_list', 'jobs:learn', 'jobs:network']

    def location(self, item):
        from django.urls import reverse
        return reverse(item)
