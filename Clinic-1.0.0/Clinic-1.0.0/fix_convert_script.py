from pathlib import Path
file_path = Path('convert_sportzone.py')
text = file_path.read_text(encoding='utf-8')
old = "('<iframe\n          src=\"https://www.google.com/maps/embed?pb=!1m14!1m8!1m3!1d48389.78314118045!2d-74.006138!3d40.710059!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x89c25a22a3bda30d%3A0xb89d1fe6bc499443!2sDowntown%20Conference%20Center!5e0!3m2!1sen!2sus!4v1676961268712!5m2!1sen!2sus\"\n          width=\"100%\" height=\"500\" style=\"border:0;\" allowfullscreen=\"\" loading=\"lazy\"\n          referrerpolicy=\"no-referrer-when-downgrade\"></iframe>',"
new = "('''<iframe\\n          src=\"https://www.google.com/maps/embed?pb=!1m14!1m8!1m3!1d48389.78314118045!2d-74.006138!3d40.710059!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x89c25a22a3bda30d%3A0xb89d1fe6bc499443!2sDowntown%20Conference%20Center!5e0!3m2!1sen!2sus!4v1676961268712!5m2!1sen!2sus\"\\n          width=\"100%\" height=\"500\" style=\"border:0;\" allowfullscreen=\"\" loading=\"lazy\"\\n          referrerpolicy=\"no-referrer-when-downgrade\"></iframe>''',"
if old not in text:
    raise SystemExit('Old substring not found')
text = text.replace(old, new)
file_path.write_text(text, encoding='utf-8')
print('patched')
