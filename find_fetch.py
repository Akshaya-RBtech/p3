with open('templates/student_portal.html', 'r', encoding='utf-8') as f:
    for i, line in enumerate(f):
        if 'fetch(' in line:
            print(f"{i+1}: {line.strip()}")
