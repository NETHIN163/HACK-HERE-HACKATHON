import glob, re, pathlib
files = glob.glob('*.html')
keywords = ['Clinic','Department','Service','Doctor','Appointment','Medical','Health','Patient','Emergency','Treatment','schedule','book','care','hospital','clinic']
for f in sorted(files):
    text = pathlib.Path(f).read_text(encoding='utf-8')
    print('FILE', f)
    for kw in keywords:
        if kw in text:
            print(' ', kw, '=>', text.count(kw))
    print('--- nav labels ---')
    patterns = ['<a href="about.html">','<a href="departments.html">','<a href="services.html">','<a href="doctors.html">','<a href="appointment.html">','<h1 class="heading-title">','<title>']
    for pat in patterns:
        if pat in text:
            matches = re.findall(r'(.{0,40}'+re.escape(pat)+'.{0,60})', text)
            for mm in matches[:3]:
                print('   ', mm)
    print()
