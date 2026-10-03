import os
import json
import uuid
import google.generativeai as genai
from dotenv import load_dotenv

from werkzeug.security import generate_password_hash, check_password_hash
import requests


load_dotenv()
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
ADMIN_SETUP_SECRET = os.environ.get("ADMIN_SETUP_SECRET", "")

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from models import db, User, MenuEntry, Vote, FoodPredictor, FoodConsumption, AIReport, ChatMessage, Announcement, Notification, Complaint, LeaveRequest, Ingredient, Feedback
from ai_engine import WasteAnalyticsAI
from datetime import datetime, timedelta

app = Flask(__name__)
from services.firebase_service import init_firebase, verify_id_token, get_firebase_config
from services.rag_service import rag_index

init_firebase()

# ── Secure configuration ──
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'wastezero-dev-secret-change-in-prod')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///hostel_waste.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

predictor = FoodPredictor()
ai_engine = WasteAnalyticsAI()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ── Helper: Get consumption data as dicts ──
def get_consumption_dicts():
    logs = FoodConsumption.query.join(MenuEntry).order_by(MenuEntry.date.asc()).all()
    return [{
        'date': log.menu.date,
        'meal_type': log.menu.meal_type,
        'items': log.menu.items,
        'event_type': log.menu.event_type,
        'prepared_qty': log.prepared_qty,
        'consumed_qty': log.consumed_qty,
        'wastage_qty': log.wastage_qty,
        'wastage_percent': log.wastage_percent,
        'total_loss': log.total_loss,
        'cost_per_unit': log.cost_per_unit
    } for log in logs]

def get_feedback_dicts():
    feedbacks = db.session.query(Vote.student_id, MenuEntry.items, Vote.reason, Vote.timestamp).\
        join(MenuEntry).filter(Vote.choice == 'No').all()
    return [{
        'student_id': f[0],
        'dish': f[1],
        'reason': f[2],
        'time': f[3].strftime('%Y-%m-%d %H:%M') if f[3] else ''
    } for f in feedbacks]

def get_menu_dicts():
    menus = MenuEntry.query.order_by(MenuEntry.date.desc()).limit(20).all()
    return [{
        'date': m.date,
        'meal_type': m.meal_type,
        'items': m.items,
        'event_type': m.event_type
    } for m in menus]

def get_vote_stats():
    """Return per-menu Yes/No vote counts for today and tomorrow."""
    today = datetime.now().strftime('%Y-%m-%d')
    tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
    menus = MenuEntry.query.filter(MenuEntry.date.in_([today, tomorrow])).all()
    stats = []
    for m in menus:
        yes = Vote.query.filter_by(menu_id=m.id, choice='Yes').count()
        no  = Vote.query.filter_by(menu_id=m.id, choice='No').count()
        stats.append({
            'date': m.date,
            'meal_type': m.meal_type,
            'items': m.items,
            'yes': yes,
            'no': no
        })
    return stats


def safe_migrate_db():
    """Safely add new columns to existing tables without losing data."""
    import sqlite3
    db_path = os.path.join(app.instance_path, 'hostel_waste.db')
    if not os.path.exists(db_path):
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check and add missing columns to User table
    try:
        cursor.execute("PRAGMA table_info(user)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'email' not in columns:
            cursor.execute("ALTER TABLE user ADD COLUMN email VARCHAR(120)")
            print("[Migration] Added 'email' column to User table.")
        
        if 'full_name' not in columns:
            cursor.execute("ALTER TABLE user ADD COLUMN full_name VARCHAR(120)")
            print("[Migration] Added 'full_name' column to User table.")
            
        cursor.execute("PRAGMA table_info(leave_request)")
        lr_columns = [col[1] for col in cursor.fetchall()]
        if lr_columns and 'admin_remarks' not in lr_columns:
            cursor.execute("ALTER TABLE leave_request ADD COLUMN admin_remarks TEXT")
            print("[Migration] Added 'admin_remarks' column to leave_request table.")
            
        conn.commit()
    except Exception as e:
        print(f"[Migration] Warning: {e}")
    finally:
        conn.close()


def init_db():
    with app.app_context():
        # Run safe migrations first
        safe_migrate_db()
        
        db.create_all()
        
        # If FoodConsumption table is empty, seed with sample data
        if FoodConsumption.query.count() == 0:
            print("FoodConsumption table is empty. Seeding fresh dataset...")
            
            import random
            from datetime import date, timedelta
            
            # Create students
            students = [
                User(username='John Doe', student_id='ST001', role='student'),
                User(username='Jane Smith', student_id='ST002', role='student'),
                User(username='Alex Jones', student_id='ST003', role='student'),
                User(username='Emily Brown', student_id='ST004', role='student'),
                User(username='Michael Green', student_id='ST005', role='student'),
                User(username='Sarah White', student_id='ST006', role='student'),
                User(username='David Black', student_id='ST007', role='student'),
                User(username='Emma Watson', student_id='ST008', role='student'),
            ]
            
            # Only add students that don't exist yet
            for s in students:
                existing = User.query.filter_by(student_id=s.student_id).first()
                if not existing:
                    db.session.add(s)
            
            breakfast_options = [
                ("Idli, Sambar, Coconut Chutney", "Normal"),
                ("Masala Dosa, Potato Masala, Sambar", "Festival"),
                ("Aloo Paratha, Curd, Pickle", "Normal"),
                ("Bread, Butter, Eggs, Tea", "Normal"),
                ("Puri Bhaji, Halwa", "Holiday")
            ]
            lunch_options = [
                ("Rice, Dal Tadka, Paneer Butter Masala, Roti, Salad", "Normal"),
                ("Veg Biryani, Raita, Gulab Jamun, Papad", "Festival"),
                ("Rice, Sambhar, Cabbage Poriyal, Rasam, Curd", "Normal"),
                ("Rajma Chawal, Jeera Rice, Curd, Salad", "Normal"),
                ("Chole Bhature, Lassi", "Holiday")
            ]
            dinner_options = [
                ("Roti, Bhindi Masala, Yellow Dal, Rice, Kheer", "Normal"),
                ("Naan, Kadai Chicken, Paneer Tikka, Veg Pulao, Ice Cream", "Festival"),
                ("Roti, Egg Curry, Dal Fry, Jeera Rice", "Normal"),
                ("Roti, Mix Veg Sabzi, Kadhi Pakora, Steamed Rice", "Normal"),
                ("Malai Kofta, Butter Roti, Dal Makhani, Pulao, Gulab Jamun", "Holiday")
            ]
            
            start_date = date.today() - timedelta(days=10)
            negative_reasons = [
                "Too oily and spicy", "Don't like this dish", "Going home for the weekend",
                "Allergic to dairy products", "Food quality was average last time",
                "Willing to eat outside with friends", "Too repetitive, served twice this week"
            ]
            
            # Seed: only if no menus exist
            if MenuEntry.query.count() == 0:
                today_str = date.today().strftime('%Y-%m-%d')
                for d_idx in range(11):
                    cur_date = (start_date + timedelta(days=d_idx)).strftime('%Y-%m-%d')
                    
                    menu_trios = [
                        ('Breakfast', breakfast_options[d_idx % len(breakfast_options)]),
                        ('Lunch', lunch_options[d_idx % len(lunch_options)]),
                        ('Dinner', dinner_options[d_idx % len(dinner_options)])
                    ]
                    
                    for meal_type, (items, event_type) in menu_trios:
                        is_published = cur_date < today_str
                        menu = MenuEntry(
                            date=cur_date,
                            meal_type=meal_type,
                            items=items,
                            event_type=event_type,
                            published=is_published
                        )
                        db.session.add(menu)
                        db.session.flush()
                        
                        all_students = User.query.filter_by(role='student').all()
                        yes_count = 0
                        for student in all_students:
                            choice_rand = random.random()
                            choice = 'Yes' if choice_rand > 0.3 else 'No'
                            reason = random.choice(negative_reasons) if choice == 'No' else None
                            if choice == 'Yes':
                                yes_count += 1
                            
                            vote = Vote(
                                student_id=student.student_id,
                                menu_id=menu.id,
                                choice=choice,
                                reason=reason
                            )
                            db.session.add(vote)
                        
                        # Record actual consumption for past days
                        if d_idx < 10:
                            guests = random.randint(0, 3)
                            total_expected = yes_count + guests
                            
                            prep_multiplier = random.choice([1.0, 1.1, 1.15, 1.25, 0.95])
                            prepared = round((total_expected * 15 * prep_multiplier), 1)
                            
                            consumption_ratio = random.uniform(0.70, 0.98)
                            consumed = round(prepared * consumption_ratio, 1)
                            
                            wastage = round(prepared - consumed, 1)
                            wastage_pct = round((wastage / prepared) * 100, 1) if prepared > 0 else 0
                            cost_val = 80.0
                            loss = round(wastage * cost_val, 2)
                            
                            recs = []
                            if wastage_pct > 20:
                                recs.append(f"CRITICAL WASTE ALERT: Wastage is high at {wastage_pct}% ({wastage} kg).")
                            elif wastage_pct > 10:
                                recs.append(f"MODERATE WASTE ALERT: Wastage is {wastage_pct}% ({wastage} kg).")
                            else:
                                recs.append(f"OPTIMAL UTILIZATION: Wastage is low at {wastage_pct}% ({wastage} kg).")
                            
                            rec_text = " | ".join(recs)
                            
                            consumption = FoodConsumption(
                                menu_id=menu.id,
                                prepared_qty=prepared,
                                consumed_qty=consumed,
                                wastage_qty=wastage,
                                wastage_percent=wastage_pct,
                                cost_per_unit=cost_val,
                                total_loss=loss,
                                recommendations=rec_text
                            )
                            db.session.add(consumption)
                
                db.session.commit()
                print("Sample data seeded successfully.")
        
        # Train predictor
        predictor.train()

# --- Routes ---

@app.route('/')
def index():
    return render_template('home.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html', type='Admin')

@app.route('/admin/setup', methods=['GET', 'POST'])
def admin_setup():
    if request.method == 'GET':
        return render_template('register.html', type='Admin')

@app.route('/student/register', methods=['GET', 'POST'])
def student_register():
    if request.method == 'GET':
        return render_template('register.html', type='Student')

@app.route('/student/login', methods=['GET', 'POST'])
def student_login():
    if request.method == 'GET':
        return render_template('login.html', type='Student')

# ── Firebase Config Endpoint ──
@app.route('/api/firebase-config')
def firebase_config():
    """Return Firebase client config for frontend initialization."""
    config = get_firebase_config()
    return jsonify(config)

# ── Auth API ──
@app.route('/api/auth/register', methods=['POST'])
def api_auth_register():
    data = request.json
    id_token = data.get('idToken')
    role = data.get('role')
    full_name = data.get('full_name')
    username = data.get('username')
    
    claims = verify_id_token(id_token)
    if not claims:
        return jsonify({'error': 'Invalid Firebase Token'}), 401
        
    email = claims.get('email')
    
    if role == 'admin':
        secret = data.get('admin_secret')
        if not ADMIN_SETUP_SECRET or secret != ADMIN_SETUP_SECRET:
            return jsonify({'error': 'Invalid setup secret.'}), 403
            
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            if existing_user.role == 'admin':
                return jsonify({'error': 'Email already registered as admin. Try logging in.'}), 400
            else:
                # Upgrade existing non-admin to admin since they have the setup secret
                existing_user.role = 'admin'
                existing_user.full_name = full_name
                db.session.commit()
                return jsonify({'success': True, 'redirect': url_for('login')})
                
        if User.query.filter_by(username=username).first():
            return jsonify({'error': 'Username already exists.'}), 400
            
        user = User(username=username, email=email, full_name=full_name, role='admin')
        db.session.add(user)
        db.session.commit()
        return jsonify({'success': True, 'redirect': url_for('login')})
        
    elif role == 'student':
        student_id = data.get('student_id')
        
        existing = User.query.filter_by(student_id=student_id).first()
        if existing:
            if existing.email:
                return jsonify({'error': 'Student ID already registered.'}), 400
            else:
                existing.username = username
                existing.full_name = full_name
                existing.email = email
                db.session.commit()
                return jsonify({'success': True, 'redirect': url_for('student_login')})
                
        existing_user_by_email = User.query.filter_by(email=email).first() if email else None
        if existing_user_by_email:
             return jsonify({'error': 'Email already registered. Try signing in instead.'}), 400
                
        if User.query.filter_by(username=username).first():
            return jsonify({'error': 'Username already exists.'}), 400
            
        user = User(username=username, full_name=full_name, email=email, student_id=student_id, role='student')
        db.session.add(user)
        db.session.commit()
        return jsonify({'success': True, 'redirect': url_for('student_login')})
        
    return jsonify({'error': 'Invalid role'}), 400

@app.route('/api/auth/login', methods=['POST'])
def api_auth_login():
    data = request.json
    id_token = data.get('idToken')
    role = data.get('role', 'student')
    
    claims = verify_id_token(id_token)
    if not claims:
        return jsonify({'error': 'Invalid Firebase Token. Unauthorized.'}), 401
        
    email = claims.get('email')
    user = User.query.filter_by(email=email).first()
    
    if not user:
        # AUTO-REGISTER user to survive Render Ephemeral disk resets!
        name = claims.get('name', email.split('@')[0])
        if role == 'student':
            student_id = email.split('@')[0].upper()
            user = User(username=name, full_name=name, email=email, student_id=student_id, role='student')
        else:
            user = User(username=name, full_name=name, email=email, role='admin')
        db.session.add(user)
        db.session.commit()
    
    login_user(user)
    
    if user.role == 'admin':
        return jsonify({'success': True, 'redirect': url_for('admin_dashboard')})
    else:
        return jsonify({'success': True, 'redirect': url_for('student_portal')})

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

# --- Admin Dashboard ---

@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    if current_user.role != 'admin':
        return redirect(url_for('index'))
    
    menus = MenuEntry.query.all()
    no_votes = db.session.query(MenuEntry.items, db.func.count(Vote.id)).join(Vote).filter(Vote.choice == 'No').group_by(MenuEntry.items).all()
    
    # Consumption Logs & Waste KPIs
    consumption_logs = FoodConsumption.query.join(MenuEntry).order_by(MenuEntry.date.desc()).all()
    
    total_prepared = sum(c.prepared_qty for c in consumption_logs)
    total_consumed = sum(c.consumed_qty for c in consumption_logs)
    total_wastage = sum(c.wastage_qty for c in consumption_logs)
    total_loss = sum(c.total_loss for c in consumption_logs)
    
    avg_waste_pct = (total_wastage / total_prepared * 100) if total_prepared > 0 else 0.0
    utilization_pct = (total_consumed / total_prepared * 100) if total_prepared > 0 else 0.0
    
    active_recommendations = []
    for c in consumption_logs:
        if c.wastage_percent > 10 and c.recommendations:
            rec_list = c.recommendations.split(" | ")
            for r in rec_list:
                if "ALERT" in r or "Action:" in r:
                    active_recommendations.append({
                        'date': c.menu.date,
                        'meal_type': c.menu.meal_type,
                        'items': c.menu.items,
                        'text': r
                    })
    
    unrecorded_menus = [m for m in menus if m.consumption is None]
    ai_reports = AIReport.query.order_by(AIReport.generated_at.desc()).limit(10).all()
    recent_votes = Vote.query.order_by(Vote.timestamp.desc()).limit(50).all()
    
    all_feedback = Feedback.query.order_by(Feedback.timestamp.desc()).all()
    all_complaints = Complaint.query.order_by(Complaint.created_at.desc()).all()
    all_leaves = LeaveRequest.query.order_by(LeaveRequest.created_at.desc()).all()
    all_ingredients = Ingredient.query.all()
    
    
    # Overview Dynamic KPIs for Today
    today_str = datetime.now().strftime('%Y-%m-%d')
    today_menus = MenuEntry.query.filter_by(date=today_str).all()
    today_menu_ids = [m.id for m in today_menus]
    
    total_students_val = User.query.filter_by(role='student').count()
    if today_menu_ids:
        max_coming = 0
        max_not_coming = 0
        for md in today_menu_ids:
            c = Vote.query.filter_by(menu_id=md, choice='Yes').count()
            nc = Vote.query.filter_by(menu_id=md, choice='No').count()
            if (c + nc) > (max_coming + max_not_coming):
                max_coming = c
                max_not_coming = nc
        coming_count = max_coming
        not_coming_count = max_not_coming
    else:
        coming_count = Vote.query.filter_by(choice='Yes').count()
        not_coming_count = Vote.query.filter_by(choice='No').count()
        if (coming_count + not_coming_count) > total_students_val and total_students_val > 0:
            scale = total_students_val / (coming_count + not_coming_count)
            coming_count = int(coming_count * scale)
            not_coming_count = int(not_coming_count * scale)
        
    pending_count_val = max(0, total_students_val - (coming_count + not_coming_count))
    response_rate = int(((coming_count + not_coming_count) / total_students_val) * 100) if total_students_val > 0 else 0
    predicted_att = coming_count + (pending_count_val // 2)
    recommended_qty = predicted_att * 0.4
    
    return render_template(
        'admin_dashboard.html',
        menus=menus,
        total_students=total_students_val,
        coming_count=coming_count,
        not_coming_count=not_coming_count,
        pending_count=pending_count_val,
        response_rate=response_rate,
        predicted_att=predicted_att,
        recommended_qty=round(recommended_qty, 1),
        no_votes=no_votes,
        consumption_logs=consumption_logs,
        unrecorded_menus=unrecorded_menus,
        total_prepared=round(total_prepared, 1),
        total_consumed=round(total_consumed, 1),
        total_wastage=round(total_wastage, 1),
        total_loss=round(total_loss, 2),
        avg_waste_pct=round(avg_waste_pct, 1),
        utilization_pct=round(utilization_pct, 1),
        active_recommendations=active_recommendations[:8],
        ai_reports=ai_reports,
        recent_votes=recent_votes,
        negative_attendance=[v for v in recent_votes if v.choice == 'No'],
        all_feedback=all_feedback,
        all_complaints=all_complaints,
        all_leaves=all_leaves,
        all_ingredients=all_ingredients
    )

@app.route('/admin/record_consumption', methods=['POST'])
@login_required
def record_consumption():
    if current_user.role != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
        
    menu_id = int(request.form.get('menu_id'))
    prepared_qty = float(request.form.get('prepared_qty'))
    consumed_qty = float(request.form.get('consumed_qty'))
    cost_per_unit = float(request.form.get('cost_per_unit', 80.0))
    
    if prepared_qty <= 0 or consumed_qty < 0:
        flash('Quantities must be positive.')
        return redirect(url_for('admin_dashboard', tab='waste'))
        
    if consumed_qty > prepared_qty:
        flash('Consumed quantity cannot exceed prepared quantity.')
        return redirect(url_for('admin_dashboard', tab='waste'))
        
    wastage_qty = round(prepared_qty - consumed_qty, 2)
    wastage_percent = round((wastage_qty / prepared_qty) * 100, 2)
    total_loss = round(wastage_qty * cost_per_unit, 2)
    
    menu = MenuEntry.query.get(menu_id)
    if not menu:
        flash('Menu entry not found.')
        return redirect(url_for('admin_dashboard', tab='waste'))
        
    no_votes_query = Vote.query.filter_by(menu_id=menu_id, choice='No').all()
    no_votes_reasons = [v.reason for v in no_votes_query if v.reason]
    
    recs = []
    if wastage_percent > 25:
        recs.append(f"CRITICAL WASTE ALERT: Wastage is extremely high at {wastage_percent}% ({wastage_qty} kg).")
        if len(no_votes_query) > 0:
            recs.append(f"Reasons noted from {len(no_votes_query)} dissenting students: '{', '.join(no_votes_reasons[:3])}'.")
        else:
            recs.append(f"High wastage despite 'Yes' votes. Action: Adjust base scale down.")
    elif wastage_percent > 10:
        recs.append(f"MODERATE WASTE ALERT: Wastage is {wastage_percent}% ({wastage_qty} kg).")
        if no_votes_reasons:
            recs.append(f"Student complaint: '{no_votes_reasons[0]}'.")
    else:
        recs.append(f"OPTIMAL UTILIZATION: Wastage is low at {wastage_percent}% ({wastage_qty} kg).")
        
    recommendations_text = " | ".join(recs)
    
    consumption = FoodConsumption.query.filter_by(menu_id=menu_id).first()
    if not consumption:
        consumption = FoodConsumption(
            menu_id=menu_id,
            prepared_qty=prepared_qty,
            consumed_qty=consumed_qty,
            wastage_qty=wastage_qty,
            wastage_percent=wastage_percent,
            cost_per_unit=cost_per_unit,
            total_loss=total_loss,
            recommendations=recommendations_text
        )
        db.session.add(consumption)
    else:
        consumption.prepared_qty = prepared_qty
        consumption.consumed_qty = consumed_qty
        consumption.wastage_qty = wastage_qty
        consumption.wastage_percent = wastage_percent
        consumption.cost_per_unit = cost_per_unit
        consumption.total_loss = total_loss
        consumption.recommendations = recommendations_text
        
    db.session.commit()
    flash('Consumption tracked successfully!')
    return redirect(url_for('admin_dashboard') + "?tab=waste")

@app.route('/api/waste_analytics')
@login_required
def get_waste_analytics():
    if current_user.role != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
        
    logs = FoodConsumption.query.join(MenuEntry).order_by(MenuEntry.date.asc()).all()
    labels = [f"{log.menu.date} ({log.menu.meal_type})" for log in logs]
    prepared = [log.prepared_qty for log in logs]
    consumed = [log.consumed_qty for log in logs]
    wastage = [log.wastage_qty for log in logs]
    
    return jsonify({
        'labels': labels,
        'prepared': prepared,
        'consumed': consumed,
        'wastage': wastage
    })

@app.route('/admin/add_menu', methods=['POST'])
@login_required
def add_menu():
    if current_user.role != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    
    date = request.form.get('date')
    meal_type = request.form.get('meal_type')
    items = request.form.get('items')
    event_type = request.form.get('event_type', 'Normal')
    action = request.form.get('action', 'publish')
    
    is_published = (action == 'publish')
    
    menu = MenuEntry(date=date, meal_type=meal_type, items=items, event_type=event_type, published=is_published)
    db.session.add(menu)
    db.session.commit()
    
    if is_published:
        flash('Menu published successfully!')
    else:
        flash('Menu saved as draft!')
    return redirect(url_for('admin_dashboard'))

@app.route('/api/predict_quantity', methods=['POST'])
@login_required
def predict_quantity():
    data = request.json
    prediction = predictor.predict(
        data['day'], data['meal'], data['event'], 
        int(data['yes_count']), int(data['guest_count'])
    )
    return jsonify({'prediction': round(prediction, 2)})

# --- Announcements & Notifications ---
@app.route('/api/announcements', methods=['GET'])
@login_required
def get_announcements():
    anns = Announcement.query.order_by(Announcement.created_at.desc()).limit(20).all()
    return jsonify([{
        'id': a.id,
        'title': a.title,
        'message': a.message,
        'category': a.category,
        'created_at': a.created_at.strftime('%Y-%m-%d %H:%M')
    } for a in anns])

@app.route('/api/announcements/create', methods=['POST'])
@login_required
def create_announcement():
    if current_user.role != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    category = request.form.get('category')
    title = request.form.get('title')
    message = request.form.get('message')
    
    ann = Announcement(title=title, message=message, category=category, created_by=current_user.username)
    db.session.add(ann)
    
    # Broadcast to all students
    students = User.query.filter_by(role='student').all()
    for s in students:
        notif = Notification(user_id=s.id, title=title, message=message[:150] + "..." if len(message)>150 else message)
        db.session.add(notif)
        
    db.session.commit()
    return jsonify({'success': True})

@app.route('/api/announcements/ai-rewrite', methods=['POST'])
@login_required
def rewrite_announcement():
    if current_user.role != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    draft = request.json.get('draft')
    title = request.json.get('title')
    if not GEMINI_API_KEY:
        return jsonify({'error': 'Gemini API not configured.'}), 400
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
        payload = {
            "contents": [{"parts": [{"text": f"Rewrite the following draft announcement to clearly and professionally inform students in a hostel. Keep facts. \nTitle: {title}\nDraft: {draft}"}]}]
        }
        resp = requests.post(url, json=payload).json()
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
        return jsonify({'error': str(e)}), 500

@app.route('/api/notifications', methods=['GET'])
@login_required
def get_notifications():
    if current_user.role != 'student':
        return jsonify({'error': 'Unauthorized'}), 403
    notifs = Notification.query.filter_by(user_id=current_user.id).order_by(Notification.created_at.desc()).limit(15).all()
    unread = sum(1 for n in notifs if not n.is_read)
    data = [{'id': n.id, 'title': n.title, 'message': n.message, 'is_read': n.is_read, 'created_at': n.created_at.strftime('%Y-%m-%d %H:%M')} for n in notifs]
    return jsonify({'notifications': data, 'unread_count': unread})

@app.route('/api/notifications/read-all', methods=['POST'])
@login_required
def read_all_notifications():
    if current_user.role != 'student':
        return jsonify({'error': 'Unauthorized'}), 403
    Notification.query.filter_by(user_id=current_user.id, is_read=False).update({'is_read': True})
    db.session.commit()
    return jsonify({'success': True})


# --- Student Portal ---

@app.route('/api/predict/evaluate')
@login_required
def evaluate_model():
    if current_user.role != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    return jsonify(predictor.evaluate())

@app.route('/student/portal')
@login_required
def student_portal():
    if current_user.role != 'student':
        return redirect(url_for('index'))
    
    tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
    today = datetime.now().strftime('%Y-%m-%d')
    
    upcoming_menus = MenuEntry.query.filter(MenuEntry.date.in_([today, tomorrow]), MenuEntry.published == True).all()
    
    my_votes = Vote.query.filter_by(student_id=current_user.student_id).all()
    vote_dict = {v.menu_id: v.choice for v in my_votes}
    
    # Build groupings and parsed dates for the Calendar Table Scroller
    grouped_menus = {}
    date_pills = []
    
    for m in upcoming_menus:
        if m.date not in grouped_menus:
            grouped_menus[m.date] = {}
            # Build pretty date dictionary safely in Python instead of Jinja
            p_date = datetime.strptime(m.date, '%Y-%m-%d')
            date_pills.append({
                'date_str': m.date,
                'dow': p_date.strftime('%a'),
                'day': p_date.strftime('%d')
            })
        grouped_menus[m.date][m.meal_type] = m
    
    # Sort date pills incrementally
    date_pills = sorted(date_pills, key=lambda x: x['date_str'])
    
    return render_template('student_portal.html', menus=upcoming_menus, vote_dict=vote_dict, today=today, tomorrow=tomorrow, grouped_menus=grouped_menus, date_pills=date_pills)
    
@app.route('/api/menu_stats/<int:menu_id>')
@login_required
def menu_stats(menu_id):
    if current_user.role != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    
    yes_count = Vote.query.filter_by(menu_id=menu_id, choice='Yes').count()
    menu = MenuEntry.query.get(menu_id)
    
    if not menu:
        return jsonify({'error': 'Menu not found'}), 404
        
    return jsonify({
        'yes_count': yes_count,
        'day': datetime.strptime(menu.date, '%Y-%m-%d').strftime('%A'),
        'meal': menu.meal_type,
        'event': menu.event_type
    })

@app.route('/student/vote', methods=['POST'])
@login_required
def vote():
    data = request.json
    menu_id = data.get('menu_id')
    choice = data.get('choice')
    reason = data.get('reason', '')
    
    if not menu_id:
        return jsonify({'error': 'Menu ID is required.'}), 400
        
    existing_vote = Vote.query.filter_by(student_id=current_user.student_id, menu_id=menu_id).first()
    if existing_vote:
        return jsonify({'error': 'You have already voted for this meal.'}), 400
    else:
        vote_record = Vote(student_id=current_user.student_id, menu_id=menu_id, choice=choice, reason=reason)
        db.session.add(vote_record)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Vote submitted!'})

@app.route('/api/analytics')
@login_required
def get_analytics():
    if current_user.role != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    
    dish_analytics = db.session.query(MenuEntry.items, db.func.count(Vote.id)).\
        join(Vote).filter(Vote.choice == 'No').\
        group_by(MenuEntry.items).all()
        
    labels = [d[0] for d in dish_analytics]
    counts = [d[1] for d in dish_analytics]
    
    feedback = db.session.query(Vote.student_id, MenuEntry.items, Vote.reason, Vote.timestamp).\
        join(MenuEntry).filter(Vote.choice == 'No').all()
    feedback_data = [{'student_id': f[0], 'dish': f[1], 'reason': f[2], 'time': f[3].strftime('%Y-%m-%d %H:%M') if f[3] else ''} for f in feedback]

    return jsonify({
        'labels': labels,
        'counts': counts,
        'feedback': feedback_data
    })


# ═══════════════════════════════════════════════
# AGENTIC AI API ENDPOINTS
# ═══════════════════════════════════════════════

@app.route('/api/ai/chat', methods=['POST'])
@login_required
def ai_chat():
    """AI Chatbot endpoint — uses Gemini LLM with RAG, fallback to rule-based."""
    data = request.json
    message = data.get('message', '')
    session_id = data.get('session_id', str(uuid.uuid4()))

    if not message.strip():
        return jsonify({'error': 'Empty message'}), 400

    consumption_logs = get_consumption_dicts()
    feedbacks = get_feedback_dicts()
    menu_data = get_menu_dicts()

    user_role = getattr(current_user, 'role', 'student')
    student_id = getattr(current_user, 'student_id', None)
    vote_stats = get_vote_stats() if user_role == 'student' else None
    
    # Save user message
    user_msg = ChatMessage(session_id=session_id, role='user', content=message)
    db.session.add(user_msg)

    response_text = ""
    msg_type = "text"
    
    # Try Gemini LLM first if available
    if GEMINI_API_KEY:
        try:
            genai.configure(api_key=GEMINI_API_KEY)
            gemini_model = genai.GenerativeModel('gemini-1.5-flash')
            
            context = "You are WasteZero AI, a specialized assistant for a hostel food-waste management app.\n"
            context += "You must use the following ACTUAL real-time data to answer data-related questions.\n"
            
            if user_role == 'admin':
                logs_summary = [f"{l['date']}: {l['meal_type']} wasted {l['wastage_percent']}% (Cost loss: {l['total_loss']})" for l in consumption_logs[-10:]]
                context += f"Last 10 Consumption Logs: {logs_summary}\n"
                context += f"Menus: {menu_data[:5]}\n"
                context += f"Feedback Summary: {[f['reason'] for f in feedbacks[:10]]}\n"
            else:
                context += f"Upcoming Menus: {menu_data[:5]}\n"
                context += "You are talking to a student. Focus on menu info, diet tips, and voting."
                if vote_stats:
                    context += f"\nCurrent Vote Stats: {vote_stats[:3]}\n"
                    
            if user_role == 'admin':
                recent_complaints = Complaint.query.order_by(Complaint.created_at.desc()).limit(5).all()
                context += f"| Admin Dash - Recent Complaints: {[{'id':c.id, 'category':c.category, 'status':c.status} for c in recent_complaints]}\n"
                recent_leaves = LeaveRequest.query.order_by(LeaveRequest.created_at.desc()).limit(5).all()
                context += f"| Admin Dash - Recent Leaves: {[{'id':l.id, 'status':l.status, 'dates':l.start_date+' to '+l.end_date} for l in recent_leaves]}\n"
                inventory = Ingredient.query.all()
                context += f"| Admin Dash - Inventory: {[{'item':i.name, 'qty':i.quantity} for i in inventory]}\n"
                recent_anns = Announcement.query.order_by(Announcement.created_at.desc()).limit(3).all()
                context += f"| Admin Dash - Announcements: {[{'title':a.title, 'msg':a.message} for a in recent_anns]}\n"
            else:
                my_complaints = Complaint.query.filter_by(student_id=student_id).order_by(Complaint.created_at.desc()).limit(3).all()
                context += f"| Student Dash - My Complaints: {[{'category':c.category, 'status':c.status} for c in my_complaints]}\n"
                my_leaves = LeaveRequest.query.filter_by(student_id=student_id).order_by(LeaveRequest.created_at.desc()).limit(3).all()
                context += f"| Student Dash - My Leaves: {[{'status':l.status, 'dates':l.start_date+' to '+l.end_date} for l in my_leaves]}\n"

            context += "\nDo not invent statistics or attendance numbers. If you don't know, say so based on the data provided."
            
            # Use RAG to fetch relevant context
            if not rag_index.is_built:
                rag_index.build_index(feedbacks)
            
            rag_results = rag_index.retrieve(message, top_k=5)
            if rag_results:
                context += "\n\nRelated Historical Semantic Context (RAG):\n"
                for res in rag_results:
                    context += f"- {res['text']} (Match: {round(res['score'], 2)})\n"
            
            prompt = f"System Context: {context}\n\nUser Question: {message}"
            gemini_resp = gemini_model.generate_content(prompt)
            response_text = gemini_resp.text
        except Exception as e:
            print(f"Gemini error: {e}")
            fallback = ai_engine.chat(message, consumption_logs, feedbacks, menu_data, user_role, student_id, vote_stats)
            response_text = fallback['text']
            msg_type = fallback.get('type', 'text')
    else:
        fallback = ai_engine.chat(message, consumption_logs, feedbacks, menu_data, user_role, student_id, vote_stats)
        response_text = fallback['text']
        msg_type = fallback.get('type', 'text')

    # Save assistant response
    assistant_msg = ChatMessage(
        session_id=session_id,
        role='assistant',
        content=response_text,
        msg_type=msg_type
    )
    db.session.add(assistant_msg)
    db.session.commit()

    return jsonify({
        'response': response_text,
        'type': msg_type,
        'session_id': session_id,
        'timestamp': datetime.now().strftime('%I:%M %p')
    })


@app.route('/api/ai/insights')
@login_required
def ai_insights():
    """Get comprehensive AI insights."""
    consumption_logs = get_consumption_dicts()
    feedbacks = get_feedback_dicts()

    clusters = ai_engine.cluster_meals(consumption_logs)
    forecast = ai_engine.forecast_waste(consumption_logs)
    anomalies = ai_engine.detect_anomalies(consumption_logs)
    feedback_analysis = ai_engine.analyze_feedback(feedbacks)
    recommendations = ai_engine.generate_smart_recommendations(consumption_logs, feedbacks)

    return jsonify({
        'clusters': clusters,
        'forecast': forecast,
        'anomalies': anomalies,
        'feedback_analysis': feedback_analysis,
        'recommendations': recommendations
    })


@app.route('/api/ai/generate_report', methods=['POST'])
@login_required
def generate_ai_report():
    """Generate and save an AI-powered report."""
    if current_user.role != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403

    data = request.json
    period = data.get('period', 'weekly')

    consumption_logs = get_consumption_dicts()
    feedbacks = get_feedback_dicts()

    report = ai_engine.generate_report(consumption_logs, feedbacks, period)

    db_report = AIReport(
        title=report['title'],
        period=report['period'],
        content=report['content'],
        summary=report.get('summary', ''),
        metrics_json=json.dumps(report.get('metrics', {})),
        generated_at=datetime.now()
    )
    db.session.add(db_report)
    db.session.commit()

    return jsonify({
        'id': db_report.id,
        'title': report['title'],
        'content': report['content'],
        'summary': report.get('summary', ''),
        'metrics': report.get('metrics', {}),
        'generated_at': report['generated_at']
    })


@app.route('/api/ai/reports')
@login_required
def list_ai_reports():
    """List all generated AI reports."""
    reports = AIReport.query.order_by(AIReport.generated_at.desc()).limit(20).all()
    return jsonify({
        'reports': [{
            'id': r.id,
            'title': r.title,
            'period': r.period,
            'summary': r.summary,
            'generated_at': r.generated_at.strftime('%Y-%m-%d %H:%M')
        } for r in reports]
    })


@app.route('/api/ai/report/<int:report_id>')
@login_required
def get_ai_report(report_id):
    """Get a specific AI report by ID."""
    report = AIReport.query.get(report_id)
    if not report:
        return jsonify({'error': 'Report not found'}), 404

    return jsonify({
        'id': report.id,
        'title': report.title,
        'period': report.period,
        'content': report.content,
        'summary': report.summary,
        'metrics': json.loads(report.metrics_json) if report.metrics_json else {},
        'generated_at': report.generated_at.strftime('%Y-%m-%d %H:%M')
    })


@app.route('/api/ai/recommendations')
@login_required
def ai_recommendations():
    """Get smart AI recommendations."""
    consumption_logs = get_consumption_dicts()
    feedbacks = get_feedback_dicts()
    recommendations = ai_engine.generate_smart_recommendations(consumption_logs, feedbacks)
    return jsonify({'recommendations': recommendations})
    
@app.route('/api/ai/chat_history')
@login_required
def chat_history():
    """Get chat history for a session."""
    session_id = request.args.get('session_id', '')
    if not session_id:
        return jsonify({'messages': []})

    messages = ChatMessage.query.filter_by(session_id=session_id).order_by(ChatMessage.timestamp.asc()).all()
    return jsonify({
        'messages': [{
            'role': m.role,
            'content': m.content,
            'type': m.msg_type,
            'timestamp': m.timestamp.strftime('%I:%M %p')
        } for m in messages]
    })


# ── Health Check ──
@app.route('/api/health')
def health_check():
    return jsonify({
        'status': 'ok',
        'service': 'WasteZero API',
        'timestamp': datetime.now().isoformat()
    })


# Initialize database and AI models for production (Gunicorn) & local
try:
    init_db()
except Exception as e:
    print(f"Warning: Database initialization failed during boot: {e}")



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
        reqs = db.session.query(LeaveRequest, User).outerjoin(User, LeaveRequest.student_id == User.student_id).order_by(LeaveRequest.created_at.desc()).all()
    else:
        reqs = db.session.query(LeaveRequest, User).outerjoin(User, LeaveRequest.student_id == User.student_id).filter(LeaveRequest.student_id == current_user.student_id).order_by(LeaveRequest.created_at.desc()).all()
    
    return jsonify([{
        "id": r[0].id,
        "student_id": r[0].student_id,
        "student_name": r[1].full_name if r[1] and r[1].full_name else (r[1].username if r[1] else r[0].student_id),
        "start_date": r[0].start_date,
        "end_date": r[0].end_date,
        "type": r[0].leave_type,
        "reason": r[0].reason,
        "status": r[0].status,
        "admin_remarks": r[0].admin_remarks or '',
        "created_at": r[0].created_at.strftime('%Y-%m-%d %H:%M') if r[0].created_at else ''
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
    if 'admin_remarks' in data:
        leave.admin_remarks = data.get('admin_remarks')
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
                v = Vote.query.filter_by(student_id=leave.student_id, menu_id=m.id).first()
                if not v:
                    v = Vote(student_id=leave.student_id, menu_id=m.id, choice='No', reason='Approved Hostel Leave')
                    db.session.add(v)
                else:
                    v.choice = 'No'
                    v.reason = 'Approved Hostel Leave'
            curr_date += delta
        db.session.commit()
        
    u = User.query.filter_by(student_id=leave.student_id, role='student').first()
    if u:
        n = Notification(user_id=u.id, title="Leave Request Update", message=f"Your leave request from {leave.start_date} to {leave.end_date} has been {leave.status}.")
        db.session.add(n)
        db.session.commit()

    return jsonify({"success": True})

@app.route('/api/announcements/send', methods=['POST'])
@login_required
def send_announcement():
    if current_user.role != 'admin':
        return jsonify({"error": "Unauthorized"}), 403
    data = request.json
    title = data.get('title', 'New Announcement')
    message = data.get('message', '')
    category = data.get('category', 'General')
    
    students = User.query.filter_by(role='student').all()
    count = 0
    for s in students:
        n = Notification(user_id=s.id, title=title, message=message)
        db.session.add(n)
        count += 1
        
    ann = Announcement(title=title, message=message, category=category, created_by=current_user.username)
    db.session.add(ann)
    db.session.commit()
    return jsonify({"success": True, "message": f"Broadcast sent to {count} students."})

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


@app.errorhandler(500)
def internal_error(e):
    import traceback
    return "<pre>" + traceback.format_exc() + "</pre>", 500

@app.route('/ping')
def ping():
    return jsonify({"status": "alive"}), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
