import re
with open('templates/admin_dashboard.html', 'r', encoding='utf-8') as f:
    text = f.read()

variables = re.findall(r'{{(.*?)}}', text)
for i, v in enumerate(variables):
    print(f"{i}: {v.strip()}")
