import sys
with open('app.py', encoding='utf-8') as f:
    for i, line in enumerate(f):
        if 'genai' in line or 'GEMINI' in line:
            print(f"{i+1}: {line.strip()}")
        if 'def ai_meal_assistant' in line:
            print(f"{i+1}: {line.strip()}")
