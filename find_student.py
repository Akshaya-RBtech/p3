import sys

with open('templates/student_portal.html', encoding='utf-8') as f:
    text = f.read()

# I will write a simple python script to search for keywords in student portal and print the lines
for i, line in enumerate(text.splitlines()):
    if 'Attendance' in line or 'attendance' in line or 'Weekly' in line or 'Leave Request' in line or 'Complaint' in line:
        print(f"{i+1}: {line.strip()}")
