from pathlib import Path

content = Path('index.html').read_text(encoding='utf-8')

replacements = [
    # Hero stats
    ('Patients Treated', 'Products Sold'),
    ('Medical Experts', 'Trusted Brands'),
    
    # About section
    ('For over two decades, we\'ve been dedicated to providing exceptional healthcare that\n                combines cutting-edge medical technology with the personal touch our patients deserve.',
     'For over two decades, SportZone has been the trusted source for premium sports equipment and performance apparel that athletes depend on.'),
    ('Our multidisciplinary team of specialists works collaboratively to ensure every patient receives\n                comprehensive care tailored to their unique needs. From preventive services to complex procedures, we\n                maintain the highest standards of medical excellence while fostering an environment of trust and\n                healing.',
     'We combine expert product curation, premium supplies, and exceptional service to help fitness enthusiasts and competitive athletes perform at their best.'),
    ('Patients Served', 'Customers Served'),
    ('Medical Specialists', 'Premium Brands'),
    ('24/7 Emergency Care\n                    <p>Always here when you need us most', '24/7 Customer Support\n                    <p>Always ready to assist you'),
    
    # Featured Departments → Featured Products
    ('<h2>Featured Departments</h2>\n        <p>Necessitatibus eius consequatur ex aliquid fuga eum quidem sint consectetur velit</p>',
     '<h2>Featured Products</h2>\n        <p>Browse our curated selection of premium sports equipment and performance gear</p>'),
    ('Cardiovascular Medicine', 'Cricket Equipment'),
    ('Advanced diagnostic imaging and interventional procedures for comprehensive heart health management\n                  with personalized treatment protocols.',
     'Premium willow bats and cricket gear engineered for power, precision, and match-winning performance.'),
    ('24/7 Emergency Cardiac Care', 'Fast Delivery & Support'),
    ('Minimally Invasive Procedures', 'Premium Quality Equipment'),
    ('Explore Cardiology', 'Explore Cricket Gear'),
    
    ('Neurological Sciences', 'Running Shoes'),
    ('Cutting-edge neuroimaging and neurosurgical expertise for complex brain and spinal cord conditions\n                  with innovative treatment approaches.',
     'Performance running shoes designed for speed, comfort, and reliability across all distances and terrains.'),
    ('Advanced Brain Imaging', 'Lightweight Design'),
    ('Robotic Surgery', 'Premium Cushioning'),
    ('Explore Neurology', 'Explore Running Shoes'),
    
    ('Orthopedic Surgery', 'Football Equipment'),
    ('Comprehensive musculoskeletal care utilizing advanced arthroscopic techniques and joint replacement\n                procedures.',
     'Professional football gear engineered for training, matches, and competitive play.'),
    ('Sports Medicine\n                <li>Joint Replacement\n                <li>Spine Surgery', 'Match-Grade Balls\n                <li>Football Boots\n                <li>Team Jerseys'),
    
    ('Pediatric Care', 'Basketball Equipment'),
    ('Child-centered healthcare services from newborn to adolescence with family-focused treatment\n                approaches.',
     'Professional basketball gear for court performance, precision shooting, and competitive play.'),
    ('Neonatal Intensive Care\n                <li>Developmental Pediatrics\n                <li>Pediatric Surgery', 'Premium Basketballs\n                <li>Basketball Shoes\n                <li>Protective Gear'),
    
    ('Cancer Treatment', 'Tennis Gear'),
    ('Multidisciplinary oncology program offering personalized cancer care with latest therapeutic\n                innovations.',
     'Professional tennis equipment for competitive players and enthusiasts seeking quality rackets and apparel.'),
    ('Precision Medicine\n                <li>Immunotherapy\n                <li>Radiation Oncology', 'Premium Rackets\n                <li>Tennis Balls\n                <li>Tennis Shoes'),
    
    # Emergency banner
    ('Emergency Services Available 24/7\n                <p>Our emergency department is equipped with state-of-the-art technology and staffed by board-certified\n                  emergency physicians ready to provide immediate care.',
     'Customer Support Available 24/7\n                <p>Our support team is ready to help with product selection, orders, and any questions about our gear.'),
    ('Call Emergency: (555) 123-4567', 'Contact Support: +91 9876543210'),
    
    # Featured Services
    ('Comprehensive Healthcare Excellence', 'Premium Sports Equipment Collection'),
    
    # Find A Doctor → Shop Brands
    ('<h2>Find A Doctor</h2>\n        <p>Necessitatibus eius consequatur ex aliquid fuga eum quidem sint consectetur velit</p>',
     '<h2>Popular Sports Brands</h2>\n        <p>Discover the world\'s leading sports brands trusted by athletes worldwide</p>'),
    ('Find Your Perfect Healthcare Provider\n              <p class="search-subtitle">Search through our comprehensive directory of experienced medical professionals',
     'Browse Top Brands\n              <p class="search-subtitle">Find the perfect sports brand and equipment for your athletic needs'),
    ('doctor_name', 'brand_name'),
    ('Enter doctor name', 'Enter brand name'),
    ('All Specialties\n                      <option value="">All Specialties</option>\n                      <option value="cardiology">Cardiology</option>\n                      <option value="neurology">Neurology</option>\n                      <option value="orthopedics">Orthopedics</option>\n                      <option value="pediatrics">Pediatrics</option>\n                      <option value="dermatology">Dermatology</option>\n                      <option value="oncology">Oncology</option>',
     'All Categories\n                      <option value="">All Categories</option>\n                      <option value="running">Running</option>\n                      <option value="cricket">Cricket</option>\n                      <option value="football">Football</option>\n                      <option value="basketball">Basketball</option>\n                      <option value="tennis">Tennis</option>\n                      <option value="gym">Gym Equipment</option>'),
    ('Find Doctors', 'Find Brands'),
    
    # Doctor profiles → Brand profiles
    ('Dr. Amanda Foster', 'Nike Store'),
    ('Cardiology Specialist', 'Performance Footwear'),
    ('14 years experience', 'Trusted Brand'),
    ('Dr. Marcus Johnson', 'Adidas Store'),
    ('Neurology Expert', 'Training Gear'),
    ('16 years experience', 'Global Leader'),
    ('Dr. Rachel Williams', 'Puma Store'),
    ('Pediatrics Care', 'Sports Lifestyle'),
    ('11 years experience', 'Trusted Partner'),
    ('Dr. David Chen', 'Under Armour'),
    ('Orthopedic Surgery', 'Athletic Apparel'),
    ('22 years experience', 'Innovation Leader'),
    ('Dr. Victoria Torres', 'New Balance'),
    ('Dermatology Care', 'Running Specialist'),
    ('9 years experience', 'Quality Brand'),
    ('Dr. Benjamin Lee', 'Decathlon'),
    ('Oncology Treatment', 'Sports Equipment'),
    ('19 years experience', 'Value Leader'),
    
    # View All link
    ('View All Doctors', 'View All Brands'),
    
    # CTA section
    ('Excellence in Medical Care, Every Day', 'Elevate Your Game with SportZone'),
    ('Need Immediate Medical Assistance?', 'Need Help Choosing Your Gear?'),
    ('Our emergency response team is available around the clock to provide immediate medical support when',
     'Our team is here 24/7 to help you find the perfect sports equipment and apparel for your needs'),
]

for old, new in replacements:
    content = content.replace(old, new)

Path('index.html').write_text(content, encoding='utf-8')
print('✓ Converted index.html from medical clinic to sports equipment store!')
