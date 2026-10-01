import os

print("Applying flawless fixes...")

# 1. Update models.py
models_path = 'models.py'
with open(models_path, 'r', encoding='utf-8') as f:
    models_content = f.read()

if 'class Complaint(db.Model)' not in models_content:
    new_models = '''
# ── Complaints and Leave (New Operations) ──
class Complaint(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.String(50), nullable=False)
    category = db.Column(db.String(50), nullable=False) 
    description = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default='Open') 
    admin_note = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

class LeaveRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.String(50), nullable=False)
    start_date = db.Column(db.String(20), nullable=False)
    end_date = db.Column(db.String(20), nullable=False)
    leave_type = db.Column(db.String(50), nullable=True) 
    reason = db.Column(db.String(200), nullable=True)
    status = db.Column(db.String(20), default='Pending') 
    created_at = db.Column(db.DateTime, server_default=db.func.now())

# ── Inventory & Feedback ──
class Ingredient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Float, nullable=False)
    unit = db.Column(db.String(20), nullable=False) 
    min_stock = db.Column(db.Float, default=10.0)
    last_updated = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())

class Feedback(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.String(50), nullable=False)
    menu_id = db.Column(db.Integer, db.ForeignKey('menu_entry.id'), nullable=False)
    rating = db.Column(db.String(20), nullable=False) 
    comments = db.Column(db.Text, nullable=True)
    timestamp = db.Column(db.DateTime, server_default=db.func.now())
'''
    with open(models_path, 'a', encoding='utf-8') as f:
        f.write(new_models)
    
    # Also fix imports and MenuEntry kitchen_status if missing in models.py
    if 'kitchen_status = db.Column' not in models_content:
        # We find MenuEntry class and insert it. Or just append it using regex.
        import re
        with open(models_path, 'r', encoding='utf-8') as f:
            mc = f.read()
        mc = re.sub(r'(class MenuEntry\(db\.Model\):.*?published = db\.Column\(db\.Boolean, default=True\))', r'\1\n    kitchen_status = db.Column(db.String(50), default="Planned")', mc, flags=re.DOTALL)
        with open(models_path, 'w', encoding='utf-8') as f:
            f.write(mc)


# 2. Update app.py
app_path = 'app.py'
with open(app_path, 'r', encoding='utf-8') as f:
    ac = f.read()

# Fix imports
if 'Complaint, LeaveRequest, Ingredient, Feedback' not in ac:
    ac = ac.replace('Announcement, Notification', 'Announcement, Notification, Complaint, LeaveRequest, Ingredient, Feedback')

if 'def handle_complaints():' not in ac:
    routes = '''

# ── COMPLAINTS & LEAVE PIPELINE ──

@app.route('/api/complaints', methods=['GET', 'POST'])
@login_required
def handle_complaints():
    if request.method == 'POST':
        if current_user.role != 'student':
            return jsonify({"error": "Unauthorized"}), 403
        data = request.json
        c = Complaint(
            student_id=current_user.student_id,
            category=data.get('category'),
            description=data.get('description'),
            status='Open'
        )
        db.session.add(c)
        db.session.commit()
        return jsonify({"success": True, "message": "Complaint submitted successfully."})
    
    if current_user.role == 'admin':
        reqs = Complaint.query.order_by(Complaint.created_at.desc()).all()
    else:
        reqs = Complaint.query.filter_by(student_id=current_user.student_id).order_by(Complaint.created_at.desc()).all()
    
    return jsonify([{
        "id": r.id,
        "student_id": r.student_id,
        "category": r.category,
        "description": r.description,
        "status": r.status,
        "admin_note": r.admin_note,
        "created_at": r.created_at.strftime('%Y-%m-%d %H:%M')
    } for r in reqs])

@app.route('/api/complaints/<int:complaint_id>/update', methods=['POST'])
@login_required
def update_complaint(complaint_id):
    if current_user.role != 'admin':
        return jsonify({"error": "Unauthorized"}), 403
    complaint = Complaint.query.get(complaint_id)
    if not complaint:
        return jsonify({"error": "Not Found"}), 404
        
    data = request.json
    complaint.status = data.get('status', complaint.status)
    complaint.admin_note = data.get('admin_note', complaint.admin_note)
    db.session.commit()
    
    u = User.query.filter_by(student_id=complaint.student_id, role='student').first()
    if u:
        n = Notification(
            user_id=u.id,
            title="Complaint Update",
            message=f"Your complaint regarding '{complaint.category}' is now {complaint.status}."
        )
        db.session.add(n)
        db.session.commit()

    return jsonify({"success": True})

@app.route('/api/leave', methods=['GET', 'POST'])
@login_required
def handle_leave():
    if request.method == 'POST':
        if current_user.role != 'student':
            return jsonify({"error": "Unauthorized"}), 403
        data = request.json
        c = LeaveRequest(
            student_id=current_user.student_id,
            start_date=data.get('start_date'),
            end_date=data.get('end_date'),
            leave_type=data.get('type', 'Other'),
            reason=data.get('reason'),
            status='Pending'
        )
        db.session.add(c)
        db.session.commit()
        return jsonify({"success": True, "message": "Leave request submitted."})
    
    if current_user.role == 'admin':
        reqs = LeaveRequest.query.order_by(LeaveRequest.created_at.desc()).all()
    else:
        reqs = LeaveRequest.query.filter_by(student_id=current_user.student_id).order_by(LeaveRequest.created_at.desc()).all()
    
    return jsonify([{
        "id": r.id,
        "student_id": r.student_id,
        "start_date": r.start_date,
        "end_date": r.end_date,
        "reason": r.reason,
        "status": r.status,
        "created_at": r.created_at.strftime('%Y-%m-%d %H:%M')
    } for r in reqs])

@app.route('/api/leave/<int:leave_id>/update', methods=['POST'])
@login_required
def update_leave(leave_id):
    if current_user.role != 'admin':
        return jsonify({"error": "Unauthorized"}), 403
    leave = LeaveRequest.query.get(leave_id)
    if not leave:
        return jsonify({"error": "Not Found"}), 404
    data = request.json
    leave.status = data.get('status', leave.status)
    db.session.commit()
    
    if leave.status == 'Approved':
        start_date = datetime.strptime(leave.start_date, '%Y-%m-%d').date()
        end_date = datetime.strptime(leave.end_date, '%Y-%m-%d').date()
        delta = timedelta(days=1)
        curr_date = start_date
        while curr_date <= end_date:
            date_str = curr_date.strftime('%Y-%m-%d')
            menus = MenuEntry.query.filter_by(date=date_str, published=True).all()
            for m in menus:
                v = Vote.query.filter_by(student_id=leave.student_id, date=date_str, meal_type=m.meal_type).first()
                if not v:
                    v = Vote(student_id=leave.student_id, date=date_str, meal_type=m.meal_type)
                    db.session.add(v)
                v.vote = 'no'
                v.skip_reason = 'Approved Hostel Leave'
            curr_date += delta
        db.session.commit()
        
    u = User.query.filter_by(student_id=leave.student_id, role='student').first()
    if u:
        n = Notification(user_id=u.id, title="Leave Request Update", message=f"Your leave request from {leave.start_date} to {leave.end_date} has been {leave.status}.")
        db.session.add(n)
        db.session.commit()

    return jsonify({"success": True})

@app.route('/api/inventory', methods=['GET'])
@login_required
def get_inventory():
    if current_user.role != 'admin':
        return jsonify({"error": "Unauthorized"}), 403
    inv = Ingredient.query.all()
    return jsonify([{"id": i.id, "name": i.name, "quantity": i.quantity, "unit": i.unit, "min_stock": i.min_stock, "last_updated": i.last_updated.strftime('%Y-%m-%d %H:%M')} for i in inv])

@app.route('/api/inventory/add', methods=['POST'])
@login_required
def add_inventory():
    if current_user.role != 'admin':
        return jsonify({"error": "Unauthorized"}), 403
    data = request.json
    ing = Ingredient(name=data.get('name'), quantity=float(data.get('quantity', 0)), unit=data.get('unit'), min_stock=float(data.get('min_stock', 10.0)))
    db.session.add(ing)
    db.session.commit()
    return jsonify({"success": True})

@app.route('/api/inventory/<int:ing_id>/update', methods=['POST'])
@login_required
def update_inventory(ing_id):
    if current_user.role != 'admin':
        return jsonify({"error": "Unauthorized"}), 403
    ing = Ingredient.query.get(ing_id)
    if not ing: return jsonify({"error": "Not Found"}), 404
    data = request.json
    if 'quantity' in data: ing.quantity = float(data['quantity'])
    if 'min_stock' in data: ing.min_stock = float(data['min_stock'])
    db.session.commit()
    return jsonify({"success": True})

@app.route('/api/feedback', methods=['POST'])
@login_required
def submit_feedback():
    if current_user.role != 'student': return jsonify({"error": "Unauthorized"}), 403
    data = request.json
    fb = Feedback(student_id=current_user.student_id, menu_id=data.get('menu_id'), rating=data.get('rating'), comments=data.get('comments', ''))
    db.session.add(fb)
    db.session.commit()
    return jsonify({"success": True})

@app.route('/api/menu/<int:menu_id>/status', methods=['POST'])
@login_required
def update_kitchen_status(menu_id):
    if current_user.role != 'admin': return jsonify({"error": "Unauthorized"}), 403
    m = MenuEntry.query.get(menu_id)
    if not m: return jsonify({"error": "Not found"}), 404
    m.kitchen_status = request.json.get('kitchen_status', m.kitchen_status)
    db.session.commit()
    return jsonify({"success": True})

'''
    # Append routes right before if __name__ == '__main__':
    # Or just to the end if not there
    ac = ac.replace('if __name__ == \x27__main__\x27:', routes + '\\n\\nif __name__ == \x27__main__\x27:')
    with open(app_path, 'w', encoding='utf-8') as f:
        f.write(ac)

print("Models and App fixed!")
