with open('ai_engine.py', encoding='utf-8') as f:
    for i, line in enumerate(f):
        if 'def chat(' in line:
            print(f"{i+1}: {line.strip()}")
