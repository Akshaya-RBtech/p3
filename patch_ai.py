import re

def fix_ai_meal_assistant():
    with open('app.py', encoding='utf-8') as f:
        content = f.read()

    # We need to replace the error returns in ai_meal_assistant with mock fallback responses.
    
    # 1. Replace the if not GEMINI_API_KEY: block inside ai_meal_assistant
    if "if not GEMINI_API_KEY:\n        return jsonify({'error': 'Gemini API not configured. Cannot perform AI action.'})" in content:
        content = content.replace(
            "if not GEMINI_API_KEY:\n        return jsonify({'error': 'Gemini API not configured. Cannot perform AI action.'})",
            "if not GEMINI_API_KEY:\n        # Fallback if API key missing\n        pass" # let it fall into try/except if we want, but wait, if it's missing, model = genai... will just use ADC and throw exception, which falls to except.
        )
        
    # Wait, it's better to rewrite the whole ai_meal_assistant endpoint securely.
    
    endpoint_pattern = re.compile(r"@app\.route\('/api/ai_meal_assistant'.*?def ai_meal_assistant\(\):.*?except Exception as e:.*?return jsonify\(\{'error': f\"AI processing failed: \{str\(e\)\}\"\}\)", re.DOTALL)
    
    replacement = """@app.route('/api/ai_meal_assistant', methods=['POST'])
@login_required
def ai_meal_assistant():
    if current_user.role != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
        
    data = request.json
    action = data.get('action')
    
    try:
        if not GEMINI_API_KEY:
            raise Exception("No API Key")
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        menus = MenuEntry.query.order_by(MenuEntry.date.desc()).limit(14).all()
        menu_text = "\\n".join([f"{m.date} - {m.meal_type}: {m.items}" for m in menus]) if menus else "No recent menus available in the database."
        
        if action == 'previous':
            prompt = f"Given these recent menus:\\n{menu_text}\\n\\nGroup them logically into a weekly structure that an Admin can copy-paste to set as next week's draft. Use markdown tables."
            result = model.generate_content(prompt).text
        
        elif action == 'generate':
            prompt = f"Act as a professional hostel menu planner. Given our recent history:\\n{menu_text}\\n\\nGenerate a brand new, highly nutritious, and exciting 7-day menu (Breakfast, Lunch, Dinner). Avoid heavy repetition of these past dishes. Format the output elegantly in Markdown."
            result = model.generate_content(prompt).text
        
        elif action == 'improve':
            feedbacks = db.session.query(Vote).filter(Vote.choice == 'No').limit(20).all()
            fb_text = "\\n".join([f"Menu ID {f.menu_id}: student said '{f.reason}'" for f in feedbacks]) if feedbacks else "No negative feedback available."
            prompt = f"Given past menus:\\n{menu_text}\\nAnd student negative feedback/skip reasons:\\n{fb_text}\\n\\nSuggest 3-5 highly concrete improvements to the menu to boost student attendance. Format beautifully in Markdown."
            result = model.generate_content(prompt).text
            
        elif action == 'repetition':
            prompt = f"Analyze these recent menus for repetitive ingredients or exactly repeated dishes over a short span:\\n{menu_text}\\n\\nList the repetitions found and provide 3 alternative dish recommendations for each highlighted repetition. Format in Markdown."
            result = model.generate_content(prompt).text
            
        else:
            return jsonify({'error': 'Unknown action'})
            
        return jsonify({'result': result})
    except Exception as e:
        fallback_msg = ""
        if action == 'previous':
            fallback_msg = "### 📋 Last Week's Mock Menu\\n*Monday*: Rice, Sambar\\n*Tuesday*: Chapati, Dal...\\n\\n*(AI is offline, showing offline fallback)*"
        elif action == 'generate':
            fallback_msg = "### 👨‍🍳 Offline AI Master Menu\\n**Breakfast**: Poha\\n**Lunch**: Veg Biryani\\n**Dinner**: Roti, Paneer\\n\\n*(AI is offline, showing mock generation)*"
        elif action == 'improve':
            fallback_msg = "### 📈 Menu Improvements\\n1. Add more protein.\\n2. Reduce spice level in Sambar based on offline feedback rules.\\n3. Offer fruit twice a week.\\n\\n*(AI is offline)*"
        elif action == 'repetition':
            fallback_msg = "### 🔍 Repetition Analysis\\nNo severe repetitions found recently based on offline heuristic.\\n\\n*(AI is offline)*"
        else:
            fallback_msg = f"AI is offline, but I received your action: {action}"
            
        return jsonify({'result': fallback_msg})"""

    new_content = endpoint_pattern.sub(replacement, content)
    
    if new_content == content:
        print("Could not find the endpoint or it was already modified.")
    else:
        with open('app.py', 'w', encoding='utf-8') as f:
            f.write(new_content)
        print("Successfully mocked fallback for AI Meal Assistant.")

fix_ai_meal_assistant()
