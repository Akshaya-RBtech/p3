with open('app.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()
with open('debug_out.txt', 'w', encoding='utf-8') as out:
    for i, line in enumerate(lines):
        if '@app.route' in line and 'login' in line:
            out.write(f"Route found: {line.strip()} at line {i+1}\n")
            for j in range(i, min(i+15, len(lines))):
                out.write(f"{j+1}: {lines[j].strip()}\n")
