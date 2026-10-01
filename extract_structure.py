import re

with open('templates/admin_dashboard.html', encoding='utf-8') as f:
    lines = f.readlines()

output = []
for i, line in enumerate(lines):
    if '<div class="card"' in line or '<!-- =' in line or 'id="content-' in line or '<div class="grid grid-cols-' in line:
        output.append(f"{i+1}: {line.strip()}")

with open('admin_cards.txt', 'w', encoding='utf-8') as f:
    f.write("\n".join(output))

with open('templates/student_portal.html', encoding='utf-8') as f:
    lines = f.readlines()

output = []
for i, line in enumerate(lines):
    if '<div class="card"' in line or '<!-- =' in line or 'id="content-' in line or '<div class="grid grid-cols-' in line:
        output.append(f"{i+1}: {line.strip()}")

with open('student_cards.txt', 'w', encoding='utf-8') as f:
    f.write("\n".join(output))

