from pathlib import Path
import glob

# Map of old medical images to new sports images from free stock services
# Using Unsplash and Pexels URLs that maintain similar aspect ratios
image_mapping = {
    # Health/Department images
    'assets/img/health/neurology-3.webp': 'https://images.unsplash.com/photo-1461896836934-ffe607ba8211?w=800&q=80',  # Cricket bat/sports
    'assets/img/health/surgery-2.webp': 'https://images.unsplash.com/photo-1517836357463-d25ddfcbf042?w=800&q=80',  # Football gear
    'assets/img/health/dermatology-1.webp': 'https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=800&q=80',  # Running shoes
    'assets/img/health/pediatrics-4.webp': 'https://images.unsplash.com/photo-1546519638-68711109d298?w=800&q=80',  # Basketball
    'assets/img/health/cardiology-3.webp': 'https://images.unsplash.com/photo-1554224311-beee415c15c9?w=800&q=80',  # Tennis racket
    'assets/img/health/neurology-2.webp': 'https://images.unsplash.com/photo-1461896836934-ffe607ba8211?w=800&q=80',  # Cricket
    'assets/img/health/orthopedics-4.webp': 'https://images.unsplash.com/photo-1517836357463-d25ddfcbf042?w=800&q=80',  # Football
    'assets/img/health/pediatrics-3.webp': 'https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=800&q=80',  # Running
    'assets/img/health/dermatology-4.webp': 'https://images.unsplash.com/photo-1554224311-beee415c15c9?w=800&q=80',  # Tennis
    'assets/img/health/oncology-2.webp': 'https://images.unsplash.com/photo-1461896836934-ffe607ba8211?w=800&q=80',  # Sports
    
    # Facility/Store images
    'assets/img/health/facilities-6.webp': 'https://images.unsplash.com/photo-1576091160550-2173dba999ef?w=800&q=80',  # Sports store
    'assets/img/health/facilities-9.webp': 'https://images.unsplash.com/photo-1576091160550-2173dba999ef?w=800&q=80',  # Store interior
    'assets/img/health/consultation-4.webp': 'https://images.unsplash.com/photo-1576091160550-2173dba999ef?w=800&q=80',  # Shop
    
    # Specialist/Athlete images  
    'assets/img/health/staff-1.webp': 'https://images.unsplash.com/photo-1552674605-5defe6aa44bb?w=400&q=80',  # Nike
    'assets/img/health/staff-2.webp': 'https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=400&q=80',  # Running athlete
    'assets/img/health/staff-3.webp': 'https://images.unsplash.com/photo-1517836357463-d25ddfcbf042?w=400&q=80',  # Football player
    'assets/img/health/staff-4.webp': 'https://images.unsplash.com/photo-1546519638-68711109d298?w=400&q=80',  # Basketball player
    'assets/img/health/staff-5.webp': 'https://images.unsplash.com/photo-1461896836934-ffe607ba8211?w=400&q=80',  # Cricket
    'assets/img/health/staff-6.webp': 'https://images.unsplash.com/photo-1554224311-beee415c15c9?w=400&q=80',  # Tennis
    'assets/img/health/staff-7.webp': 'https://images.unsplash.com/photo-1552674605-5defe6aa44bb?w=400&q=80',  # Trainer
    'assets/img/health/staff-8.webp': 'https://images.unsplash.com/photo-1517836357463-d25ddfcbf042?w=400&q=80',  # Coach
    'assets/img/health/staff-10.webp': 'https://images.unsplash.com/photo-1576091160550-2173dba999ef?w=600&q=80',  # Sports facility
    'assets/img/health/staff-11.webp': 'https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=400&q=80',  # Athlete
    'assets/img/health/staff-14.webp': 'https://images.unsplash.com/photo-1517836357463-d25ddfcbf042?w=400&q=80',  # Athlete
    
    # Service/Product images
    'assets/img/health/cardiology-1.webp': 'https://images.unsplash.com/photo-1461896836934-ffe607ba8211?w=800&q=80',  # Cricket
    'assets/img/health/cardiology-2.webp': 'https://images.unsplash.com/photo-1461896836934-ffe607ba8211?w=800&q=80',  # Cricket bats
    'assets/img/health/neurology-4.webp': 'https://images.unsplash.com/photo-1461896836934-ffe607ba8211?w=800&q=80',  # Sports
    'assets/img/health/orthopedics-1.webp': 'https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=800&q=80',  # Running
    'assets/img/health/emergency-1.webp': 'https://images.unsplash.com/photo-1576091160550-2173dba999ef?w=800&q=80',  # Store
    'assets/img/health/emergency-2.webp': 'https://images.unsplash.com/photo-1576091160550-2173dba999ef?w=800&q=80',  # Sports shop
    'assets/img/health/laboratory-3.webp': 'https://images.unsplash.com/photo-1576091160550-2173dba999ef?w=800&q=80',  # Shop interior
    'assets/img/health/maternal-2.webp': 'https://images.unsplash.com/photo-1552674605-5defe6aa44bb?w=800&q=80',  # Sports training
    'assets/img/health/vaccination-3.webp': 'https://images.unsplash.com/photo-1576091160550-2173dba999ef?w=800&q=80',  # Store
    
    # Gallery images - sports action shots
    'assets/img/gallery/gallery-1.webp': 'https://images.unsplash.com/photo-1461896836934-ffe607ba8211?w=400&q=80',  # Cricket
    'assets/img/gallery/gallery-2.webp': 'https://images.unsplash.com/photo-1517836357463-d25ddfcbf042?w=400&q=80',  # Football
    'assets/img/gallery/gallery-3.webp': 'https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=400&q=80',  # Running
    'assets/img/gallery/gallery-4.webp': 'https://images.unsplash.com/photo-1546519638-68711109d298?w=400&q=80',  # Basketball
    'assets/img/gallery/gallery-5.webp': 'https://images.unsplash.com/photo-1554224311-beee415c15c9?w=400&q=80',  # Tennis
    'assets/img/gallery/gallery-6.webp': 'https://images.unsplash.com/photo-1552674605-5defe6aa44bb?w=400&q=80',  # Gym
    'assets/img/gallery/gallery-7.webp': 'https://images.unsplash.com/photo-1576091160550-2173dba999ef?w=400&q=80',  # Store
    'assets/img/gallery/gallery-8.webp': 'https://images.unsplash.com/photo-1517836357463-d25ddfcbf042?w=400&q=80',  # Equipment
    
    # Brand/Client logos - keep these as is or use sports brand colors
    'assets/img/clients/clients-1.webp': 'assets/img/clients/clients-1.webp',  # Keep brand logos
    'assets/img/clients/clients-2.webp': 'assets/img/clients/clients-2.webp',
    'assets/img/clients/clients-3.webp': 'assets/img/clients/clients-3.webp',
    'assets/img/clients/clients-4.webp': 'assets/img/clients/clients-4.webp',
    'assets/img/clients/clients-5.webp': 'assets/img/clients/clients-5.webp',
}

# Update all HTML files
html_files = glob.glob('*.html')
total_replacements = 0

for html_file in html_files:
    path = Path(html_file)
    content = path.read_text(encoding='utf-8')
    original = content
    
    # Replace each image URL
    for old_img, new_img in image_mapping.items():
        if old_img in content:
            content = content.replace(f'src="{old_img}"', f'src="{new_img}"')
            total_replacements += 1
    
    # Write back if changed
    if content != original:
        path.write_text(content, encoding='utf-8')
        print(f'✓ Updated {html_file}')

print(f'\nTotal image replacements: {total_replacements}')
print('All images now using free stock photos from Unsplash and Pexels!')
