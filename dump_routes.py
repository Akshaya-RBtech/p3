import re
routes = []
with open('app.py', 'r', encoding='utf-8') as f:
    for i, line in enumerate(f):
        if line.strip().startswith('@app.route'):
            routes.append(f"{i+1}: {line.strip()}")

with open('routes.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(routes))
