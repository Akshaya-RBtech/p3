import re
with open('templates/admin_dashboard.html', encoding='utf-8') as f:
    text = f.read()
ids = re.findall(r'id=\"content-([a-zA-Z0-9_\-]+)\"', text)
print("Admin content IDs:", ids)

with open('templates/student_portal.html', encoding='utf-8') as f:
    text = f.read()
s_ids = re.findall(r'id=\"content-([a-zA-Z0-9_\-]+)\"', text)
print("Student content IDs:", s_ids)
