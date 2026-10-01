import os

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

old_code = """        resp = requests.post(url, json=payload).json()
        rewritten = resp.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', draft)
        return jsonify({'success': True, 'rewritten': rewritten.strip()})
    except Exception as e:
        return jsonify({'error': str(e)}), 500"""

new_code = """        resp = requests.post(url, json=payload).json()
        if 'error' in resp:
            return jsonify({'error': f"Gemini API Error: {resp['error'].get('message', 'Auth failed')}"}), 401
            
        candidates = resp.get('candidates', [])
        if not candidates:
            return jsonify({'error': 'No response generated from AI.'}), 500
            
        rewritten = candidates[0].get('content', {}).get('parts', [{}])[0].get('text', draft)
        return jsonify({'success': True, 'rewritten': rewritten.strip() if rewritten else draft})
    except requests.exceptions.RequestException as e:
        return jsonify({'error': 'Network connection to AI failed.'}), 503
    except Exception as e:
        return jsonify({'error': str(e)}), 500"""

content = content.replace(old_code, new_code)
content = content.replace("container.innerHTML = '<div class=\"text-center p-8 text-muted\"><i class=\"fas fa-bell-slash text-2xl mb-3 block\"></i>No notifications found. You\\'re all caught up!</div>';", "container.innerHTML = `<div class=\"text-center p-8 text-muted\"><i class=\"fas fa-bell-slash text-2xl mb-3 block\"></i>No notifications found. You're all caught up!</div>`;")

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

with open('templates/student_portal.html', 'r', encoding='utf-8') as f:
    content2 = f.read()
    
content2 = content2.replace("No notifications found. You're all caught up!", "No notifications found. You are all caught up!")
with open('templates/student_portal.html', 'w', encoding='utf-8') as f:
    f.write(content2)
