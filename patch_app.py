import sys
with open('app.py', 'r', encoding='utf-8') as f:
    text = f.read()

feedback_code = """
@app.route('/api/feedback', methods=['GET', 'POST'])
@login_required
def submit_feedback():
    if request.method == 'POST':
        if current_user.role != 'student': return jsonify({"error": "Unauthorized"}), 403
        data = request.json
        fb = Feedback(student_id=current_user.student_id, menu_id=data.get('menu_id'), rating=data.get('rating'), comments=data.get('comments', ''))
        db.session.add(fb)
        db.session.commit()
        return jsonify({"success": True})
    
    # GET method for Admin
    if current_user.role != 'admin':
        return jsonify({"error": "Unauthorized"}), 403
    fbs = db.session.query(Feedback, MenuEntry).join(MenuEntry).order_by(Feedback.timestamp.desc()).all()
    return jsonify([{
        "id": f.Feedback.id,
        "student_id": f.Feedback.student_id,
        "dish": f.MenuEntry.items,
        "meal": f.MenuEntry.meal_type,
        "date": f.MenuEntry.date,
        "rating": f.Feedback.rating,
        "comments": f.Feedback.comments,
        "timestamp": f.Feedback.timestamp.strftime('%Y-%m-%d %H:%M')
    } for f in fbs])
"""

import re
text = re.sub(r"@app\.route\('/api/feedback', methods=\['POST'\]\).*?return jsonify.*?success.*?True.*?\}", feedback_code.strip(), text, flags=re.DOTALL)

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(text)
print("app.py patched!")
