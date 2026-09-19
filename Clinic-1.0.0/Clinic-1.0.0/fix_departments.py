from pathlib import Path

content = Path('departments.html').read_text(encoding='utf-8')

# Fix breadcrumb
content = content.replace(
    '<li class="current">Departments</li>',
    '<li class="current">Categories</li>'
)

# Fix medical specialties section header
content = content.replace(
    '<div class="medical-specialties">',
    '<div class="sports-categories">'
)

# Replace all department tabs with sports categories
tabs_mapping = [
    # Tab buttons and IDs
    ('id="specialty-tabs"', 'id="category-tabs"'),
    ('id="neurology-tab"', 'id="cricket-tab"'),
    ('id="surgery-tab"', 'id="football-tab"'),
    ('id="dental-tab"', 'id="running-tab"'),
    ('id="ophthalmology-tab"', 'id="basketball-tab"'),
    ('id="cardiology-tab"', 'id="tennis-tab"'),
    
    # Tab hrefs
    ('href="#departments-tabs-neurology"', 'href="#departments-tabs-cricket"'),
    ('href="#departments-tabs-surgery"', 'href="#departments-tabs-football"'),
    ('href="#departments-tabs-dental"', 'href="#departments-tabs-running"'),
    ('href="#departments-tabs-ophthalmology"', 'href="#departments-tabs-basketball"'),
    ('href="#departments-tabs-cardiology"', 'href="#departments-tabs-tennis"'),
    
    # Tab controls
    ('aria-controls="departments-tabs-neurology"', 'aria-controls="departments-tabs-cricket"'),
    ('aria-controls="departments-tabs-surgery"', 'aria-controls="departments-tabs-football"'),
    ('aria-controls="departments-tabs-dental"', 'aria-controls="departments-tabs-running"'),
    ('aria-controls="departments-tabs-ophthalmology"', 'aria-controls="departments-tabs-basketball"'),
    ('aria-controls="departments-tabs-cardiology"', 'aria-controls="departments-tabs-tennis"'),
    
    # Tab pane IDs
    ('id="departments-tabs-neurology"', 'id="departments-tabs-cricket"'),
    ('id="departments-tabs-surgery"', 'id="departments-tabs-football"'),
    ('id="departments-tabs-dental"', 'id="departments-tabs-running"'),
    ('id="departments-tabs-ophthalmology"', 'id="departments-tabs-basketball"'),
    ('id="departments-tabs-cardiology"', 'id="departments-tabs-tennis"'),
    
    # Tab labels
    ('>Neurology</a>', '>Cricket Equipment</a>'),
    ('>Surgery</a>', '>Football Gear</a>'),
    ('>Dental Care</a>', '>Running Shoes</a>'),
    ('>Ophthalmology</a>', '>Basketball Equipment</a>'),
    ('>Cardiology</a>', '>Tennis Gear</a>'),
    
    # Department titles
    ('Neurological Sciences Department', 'Cricket Equipment Collection'),
    ('Surgical Services Department', 'Football Gear Collection'),
    ('Dental Care Department', 'Running Shoes Collection'),
    ('Ophthalmology Department', 'Basketball Equipment Collection'),
    ('Cardiology Department', 'Tennis Gear Collection'),
]

for old, new in tabs_mapping:
    content = content.replace(old, new)

# Replace Neurology tab content
neurology_content = '''<div class="tab-pane fade show active" id="departments-tabs-cricket" role="tabpanel"
                  aria-labelledby="cricket-tab">
                  <div class="row department-layout">
                    <div class="col-lg-4 order-lg-2">
                      <div class="department-image">
                        <img src="assets/img/health/neurology-3.webp" alt="Cricket Equipment" class="img-fluid">
                      </div>
                    </div>
                    <div class="col-lg-8 order-lg-1">
                      <div class="department-info">
                        <h2 class="department-title">Cricket Equipment Collection</h2>
                        <p class="department-description">Discover our premium cricket equipment engineered for power, precision, and exceptional performance on the field.</p>

                        <div class="row mt-4">
                          <div class="col-md-6">
                            <div class="service-item">
                              <div class="service-icon">
                                <i class="fas fa-baseball"></i>
                              </div>
                              <div class="service-content">
                                <h4>Premium Willow Bats</h4>
                                <p>Hand-selected willow for superior ball control and power delivery.</p>
                              </div>
                            </div>
                          </div>
                          <div class="col-md-6">
                            <div class="service-item">
                              <div class="service-icon">
                                <i class="fas fa-shield-alt"></i>
                              </div>
                              <div class="service-content">
                                <h4>Protective Gear</h4>
                                <p>Helmets, pads, and gloves for maximum safety and comfort.</p>
                              </div>
                            </div>
                          </div>
                          <div class="col-md-6">
                            <div class="service-item">
                              <div class="service-icon">
                                <i class="fas fa-sphere"></i>
                              </div>
                              <div class="service-content">
                                <h4>Match Balls</h4>
                                <p>Official grade cricket balls for practice and competitive play.</p>
                              </div>
                            </div>
                          </div>
                          <div class="col-md-6">
                            <div class="service-item">
                              <div class="service-icon">
                                <i class="fas fa-box"></i>
                              </div>
                              <div class="service-content">
                                <h4>Cricket Accessories</h4>
                                <p>Bags, covers, and training equipment for serious players.</p>
                              </div>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div><!-- End Cricket Tab -->'''

old_neurology = content[content.find('id="departments-tabs-cricket"'):content.find('<!-- End Neurology Tab -->')+len('<!-- End Neurology Tab -->')]
if '<!-- End Neurology Tab -->' in content:
    content = content.replace(old_neurology, neurology_content + '\n                <!-- End Cricket Tab -->')

# Replace Surgery tab content
surgery_content = '''<div class="tab-pane fade" id="departments-tabs-football" role="tabpanel" aria-labelledby="football-tab">
                  <div class="row department-layout">
                    <div class="col-lg-4 order-lg-2">
                      <div class="department-image">
                        <img src="assets/img/health/surgery-2.webp" alt="Football Gear" class="img-fluid">
                      </div>
                    </div>
                    <div class="col-lg-8 order-lg-1">
                      <div class="department-info">
                        <h2 class="department-title">Football Gear Collection</h2>
                        <p class="department-description">Complete football equipment for training, matches, and competitive play with superior quality and durability.</p>

                        <div class="row mt-4">
                          <div class="col-md-6">
                            <div class="service-item">
                              <div class="service-icon">
                                <i class="fas fa-futbol"></i>
                              </div>
                              <div class="service-content">
                                <h4>Premium Footballs</h4>
                                <p>Match-grade balls with excellent flight and control on any surface.</p>
                              </div>
                            </div>
                          </div>
                          <div class="col-md-6">
                            <div class="service-item">
                              <div class="service-icon">
                                <i class="fas fa-boot"></i>
                              </div>
                              <div class="service-content">
                                <h4>Football Boots</h4>
                                <p>Lightweight, responsive boots engineered for speed and agility.</p>
                              </div>
                            </div>
                          </div>
                          <div class="col-md-6">
                            <div class="service-item">
                              <div class="service-icon">
                                <i class="fas fa-shield-alt"></i>
                              </div>
                              <div class="service-content">
                                <h4>Protective Kits</h4>
                                <p>Shin guards, socks, and protective gear for player safety.</p>
                              </div>
                            </div>
                          </div>
                          <div class="col-md-6">
                            <div class="service-item">
                              <div class="service-icon">
                                <i class="fas fa-tshirt"></i>
                              </div>
                              <div class="service-content">
                                <h4>Team Jerseys</h4>
                                <p>Custom and official team jerseys with superior breathability.</p>
                              </div>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div><!-- End Football Tab -->'''

# Replace Dental tab content
dental_content = '''<div class="tab-pane fade" id="departments-tabs-running" role="tabpanel" aria-labelledby="running-tab">
                  <div class="row department-layout">
                    <div class="col-lg-4 order-lg-2">
                      <div class="department-image">
                        <img src="assets/img/health/dermatology-1.webp" alt="Running Shoes" class="img-fluid">
                      </div>
                    </div>
                    <div class="col-lg-8 order-lg-1">
                      <div class="department-info">
                        <h2 class="department-title">Running Shoes Collection</h2>
                        <p class="department-description">Performance running shoes designed for speed, comfort, and reliability across all distances and terrains.</p>

                        <div class="row mt-4">
                          <div class="col-md-6">
                            <div class="service-item">
                              <div class="service-icon">
                                <i class="fas fa-shoe-prints"></i>
                              </div>
                              <div class="service-content">
                                <h4>Trail Running Shoes</h4>
                                <p>Rugged grip and support for off-road terrain and mountain running.</p>
                              </div>
                            </div>
                          </div>
                          <div class="col-md-6">
                            <div class="service-item">
                              <div class="service-icon">
                                <i class="fas fa-wind"></i>
                              </div>
                              <div class="service-content">
                                <h4>Road Running Shoes</h4>
                                <p>Lightweight cushioning and responsive feel for road marathons.</p>
                              </div>
                            </div>
                          </div>
                          <div class="col-md-6">
                            <div class="service-item">
                              <div class="service-icon">
                                <i class="fas fa-star"></i>
                              </div>
                              <div class="service-content">
                                <h4>Sprint Shoes</h4>
                                <p>Minimal shoes for explosive speed and track performance.</p>
                              </div>
                            </div>
                          </div>
                          <div class="col-md-6">
                            <div class="service-item">
                              <div class="service-icon">
                                <i class="fas fa-cog"></i>
                              </div>
                              <div class="service-content">
                                <h4>Custom Fitting</h4>
                                <p>Expert shoe fitting and recommendations for your running style.</p>
                              </div>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div><!-- End Running Tab -->'''

# Replace Ophthalmology tab content
ophthalmology_content = '''<div class="tab-pane fade" id="departments-tabs-basketball" role="tabpanel"
                  aria-labelledby="basketball-tab">
                  <div class="row department-layout">
                    <div class="col-lg-4 order-lg-2">
                      <div class="department-image">
                        <img src="assets/img/health/pediatrics-4.webp" alt="Basketball Equipment" class="img-fluid">
                      </div>
                    </div>
                    <div class="col-lg-8 order-lg-1">
                      <div class="department-info">
                        <h2 class="department-title">Basketball Equipment Collection</h2>
                        <p class="department-description">Professional basketball gear engineered for court performance, precision shooting, and competitive play.</p>

                        <div class="row mt-4">
                          <div class="col-md-6">
                            <div class="service-item">
                              <div class="service-icon">
                                <i class="fas fa-basketball"></i>
                              </div>
                              <div class="service-content">
                                <h4>Premium Basketballs</h4>
                                <p>Official size and weight balls with superior grip and control.</p>
                              </div>
                            </div>
                          </div>
                          <div class="col-md-6">
                            <div class="service-item">
                              <div class="service-icon">
                                <i class="fas fa-boot"></i>
                              </div>
                              <div class="service-content">
                                <h4>Basketball Shoes</h4>
                                <p>High-top shoes with ankle support and responsive cushioning.</p>
                              </div>
                            </div>
                          </div>
                          <div class="col-md-6">
                            <div class="service-item">
                              <div class="service-icon">
                                <i class="fas fa-ring"></i>
                              </div>
                              <div class="service-content">
                                <h4>Hoops & Nets</h4>
                                <p>Professional-grade hoops and nets for training and competition.</p>
                              </div>
                            </div>
                          </div>
                          <div class="col-md-6">
                            <div class="service-item">
                              <div class="service-icon">
                                <i class="fas fa-gloves"></i>
                              </div>
                              <div class="service-content">
                                <h4>Gloves & Wrist Gear</h4>
                                <p>Protective and performance accessories for enhanced play.</p>
                              </div>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div><!-- End Basketball Tab -->'''

# Replace Cardiology tab content
cardiology_content = '''<div class="tab-pane fade" id="departments-tabs-tennis" role="tabpanel"
                  aria-labelledby="tennis-tab">
                  <div class="row department-layout">
                    <div class="col-lg-4 order-lg-2">
                      <div class="department-image">
                        <img src="assets/img/health/cardiology-3.webp" alt="Tennis Gear" class="img-fluid">
                      </div>
                    </div>
                    <div class="col-lg-8 order-lg-1">
                      <div class="department-info">
                        <h2 class="department-title">Tennis Gear Collection</h2>
                        <p class="department-description">Professional tennis equipment for competitive players and enthusiasts seeking quality rackets, balls, and apparel.</p>

                        <div class="row mt-4">
                          <div class="col-md-6">
                            <div class="service-item">
                              <div class="service-icon">
                                <i class="fas fa-tennis"></i>
                              </div>
                              <div class="service-content">
                                <h4>Premium Rackets</h4>
                                <p>High-performance rackets for competitive tennis and training.</p>
                              </div>
                            </div>
                          </div>
                          <div class="col-md-6">
                            <div class="service-item">
                              <div class="service-icon">
                                <i class="fas fa-circle"></i>
                              </div>
                              <div class="service-content">
                                <h4>Tennis Balls</h4>
                                <p>Tournament-grade balls with consistent bounce and durability.</p>
                              </div>
                            </div>
                          </div>
                          <div class="col-md-6">
                            <div class="service-item">
                              <div class="service-icon">
                                <i class="fas fa-boot"></i>
                              </div>
                              <div class="service-content">
                                <h4>Tennis Shoes</h4>
                                <p>Court-specific shoes for lateral movement and stability.</p>
                              </div>
                            </div>
                          </div>
                          <div class="col-md-6">
                            <div class="service-item">
                              <div class="service-icon">
                                <i class="fas fa-grin"></i>
                              </div>
                              <div class="service-content">
                                <h4>Tennis Apparel</h4>
                                <p>Breathable clothing and accessories for match performance.</p>
                              </div>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div><!-- End Tennis Tab -->'''

# Do the full replacements
if '<!-- End Surgery Tab -->' in content:
    start = content.find('id="departments-tabs-football"')
    end = content.find('<!-- End Surgery Tab -->')+len('<!-- End Surgery Tab -->')
    old = content[start:end]
    content = content.replace(old, surgery_content)

if '<!-- End Dental Tab -->' in content:
    start = content.find('id="departments-tabs-running"')
    end = content.find('<!-- End Dental Tab -->')+len('<!-- End Dental Tab -->')
    old = content[start:end]
    content = content.replace(old, dental_content)

if '<!-- End Ophthalmology Tab -->' in content:
    start = content.find('id="departments-tabs-basketball"')
    end = content.find('<!-- End Ophthalmology Tab -->')+len('<!-- End Ophthalmology Tab -->')
    old = content[start:end]
    content = content.replace(old, ophthalmology_content)

if '<!-- End Cardiology Tab -->' in content:
    start = content.find('id="departments-tabs-tennis"')
    end = content.find('<!-- End Cardiology Tab -->')+len('<!-- End Cardiology Tab -->')
    old = content[start:end]
    content = content.replace(old, cardiology_content)

Path('departments.html').write_text(content, encoding='utf-8')
print('Updated departments.html with sports categories')
