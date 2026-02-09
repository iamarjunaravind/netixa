import os
import django
import random
import requests
from django.core.files import File
from io import BytesIO

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'job_portal_core.settings')
django.setup()

from jobs.models import Article, ArticleCategory

def populate_images():
    print("Refining Article Images with Specific Topics...")

    # HIGHLY SPECIFIC KEYWORDS MAPPING
    # Format: 'subcategory_slug': ['keyword1', 'keyword2']
    # If subcategory slug matches, use these. If not, fallback to parent.
    
    KEYWORD_MAPPING = {
        # Marketing
        'seo': ['seo analysis', 'google search graph', 'analytics dashboard'],
        'content-marketing': ['typewriter', 'blogging', 'content strategy'],
        'social-media': ['instagram phone', 'facebook likes', 'social media influencer'],
        'email-marketing': ['email newsletter', 'mailbox', 'marketing automation'],
        'ppc': ['pay per click', 'google ads', 'digital advertising'],
        
        # Public Administration
        'public-policy': ['government building', 'policy document', 'politician'],
        'governance': ['gavel', 'law books', 'city hall'],
        'urban-planning': ['city map', 'urban construction', 'smart city'],
        
        # Healthcare
        'nursing': ['nurse', 'hospital bed', 'medical checkup'],
        'healthcare-management': ['hospital building', 'doctor meeting', 'medical records'],
        'medical-research': ['microscope', 'lab test', 'dna structure'],
        'nutrition': ['healthy food', 'vegetables', 'diet plan'],
        
        # Engineering
        'civil-engineering': ['bridge construction', 'blueprint', 'architect', 'helmet'],
        'mechanical-engineering': ['gears', 'engine', 'robotics arm', 'factory'],
        'electrical-engineering': ['circuit board', 'wires', 'power plant', 'solar panel'],
        'chemical-engineering': ['laboratory flask', 'chemical reaction', 'periodical table'],
        
        # IT Services
        'software-development': ['coding screen', 'programmer', 'matrix code', 'laptop'],
        'cloud-computing': ['server room', 'cloud database', 'datacenter'],
        'cybersecurity': ['hacker', 'digital lock', 'network security', 'firewall'],
        'data-science': ['data visualization', 'artificial intelligence', 'neural network'],
        
        # Sustainability
        'renewable-energy': ['solar panels', 'wind turbine', 'green energy'],
        'environmental-science': ['forest', 'recycling', 'climate change', 'earth'],
        
        # Business
        'human-resources': ['job interview', 'handshake', 'office team'],
        'finance': ['stock market', 'calculator', 'money', 'coins'],
        'project-management': ['kanban board', 'team meeting', 'gantt chart'],
        
        # Telecommunications
        '5g-technology': ['5g tower', 'smartphone network', 'satellite'],
        'network-infrastructure': ['optic fiber', 'network cables', 'router'],
    }
    
    DEFAULT_KEYWORDS = ['technology', 'business', 'office', 'meeting']

    # Local pool cache
    local_images = {}
    media_root = 'media/article_images_pool_v2'
    os.makedirs(media_root, exist_ok=True)

    def download_image(keyword, index):
        # Use simple reliable source
        # LoremFlickr supports keywords nicely
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

    # 1. Identify all subcategories used
    subcats = ArticleCategory.objects.exclude(parent=None)
    
    print("Downloading refined image pool...")
    for subcat in subcats:
        slug = subcat.slug
        # Find keywords
        keywords = KEYWORD_MAPPING.get(slug)
        if not keywords:
            # Fallback to parent slug if no specific map
            if subcat.parent:
                keywords = KEYWORD_MAPPING.get(subcat.parent.slug)
            
        if not keywords:
            keywords = DEFAULT_KEYWORDS
            
        # Download 3-4 images for this subcategory
        pool = []
        for i, keyword in enumerate(keywords):
             # Download 2 variations per keyword to get ~6 images per subcat
             path1 = download_image(keyword, i*10 + 1)
             if path1: pool.append(path1)
             path2 = download_image(keyword, i*10 + 2)
             if path2: pool.append(path2)
        
        local_images[slug] = pool
        print(f"  - {subcat.name} ({slug}): {len(pool)} images.")

    # 2. Update Articles
    print("\nUpdating articles with specific images...")
    articles = Article.objects.all()
    count = 0
    
    for article in articles:
        if not article.category: continue
        
        # Get specific pool
        slug = article.category.slug
        pool = local_images.get(slug)
        
        # Fallback to parent pool if subcat has no images (shouldn't happen with our logic but safety)
        if not pool and article.category.parent:
             pool = local_images.get(article.category.parent.slug)
             
        if not pool:
             # Last resort
             continue
             
        # Pick random
        img_path = random.choice(pool)
        
        with open(img_path, 'rb') as f:
            fname = os.path.basename(img_path)
            # Delete old? Django handles replacement usually, but file remains. 
            # We just overwrite the field field.
            article.image.save(fname, File(f), save=True)
            count += 1
            if count % 50 == 0:
                print(f"  - Updated {count} articles...")

    print("Done! All articles updated.")

if __name__ == '__main__':
    populate_images()
