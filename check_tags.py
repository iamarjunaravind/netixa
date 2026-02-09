import re

file_path = r'c:\Users\abc\Documents\Custom Office Templates\job_portal\templates\jobs\profile.html'
with open(file_path, 'r', encoding='utf-8') as f:
    for i, line in enumerate(f, 1):
        # find all tags in line
        tags = re.findall(r'{%\s*(if|endif|for|endfor|block|endblock|else|empty|extends|load)\b', line)
        if tags:
            print(f"Line {i}: {tags}")
        
        # Check if any tag is unclosed on this line
        if '{%' in line and '%}' not in line:
            print(f"!!! POTENTIAL SPLIT TAG on Line {i}: {line.strip()}")
        if '%}' in line and '{%' not in line:
            # could be a closing part of a split tag or just some random %}
            # But in templates, %} almost always follows {%
            pass
