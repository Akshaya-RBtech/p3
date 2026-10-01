import sys
import traceback
from app import app, db, student_portal
from flask_login import login_user
from models import User

app.config['TESTING'] = True
with app.test_request_context('/student/portal'):
    u = User(username=None, email=None, student_id='ST888', role='student') # EMPTY USERNAME & EMAIL!
    try:
        db.session.add(u)
        db.session.commit()
    except Exception:
        db.session.rollback()
        # Fallback to bypass constraint
        u.username = ""
        db.session.add(u)
        db.session.commit()
        
    login_user(u)
    try:
        print("Rendering Student Portal with EMPTY email and username...")
        html = student_portal()
        print("Success, length =", len(html))
    except Exception as e:
        print("CRASHED!")
        traceback.print_exc(file=sys.stdout)
    finally:
        db.session.delete(u)
        db.session.commit()
