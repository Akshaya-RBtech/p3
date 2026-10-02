with open('templates/student_portal.html', 'r', encoding='utf-8') as f:
    for i, line in enumerate(f):
        if 'Menu' in line or 'Calendar' in line or '<button ' in line:
            print(f"{i+1}: {line.strip()}")
