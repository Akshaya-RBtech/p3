import re

with open('templates/admin_dashboard.html', encoding='utf-8') as f:
    lines = f.readlines()

print("Admin:")
for i, line in enumerate(lines):
    if '=====' in line:
        print(f"{i+1}: {line.strip()}")

print("\n--- STUDENT PORTAL ---")
with open('templates/student_portal.html', encoding='utf-8') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if '=====' in line:
        print(f"{i+1}: {line.strip()}")
