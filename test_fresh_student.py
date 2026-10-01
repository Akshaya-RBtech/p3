import sys
import traceback
from app import app, db, student_portal
from flask_login import login_user
from models import User

app.config['TESTING'] = True
with app.test_request_context('/student/portal'):
    u = User(username='fresh_student', email='fresh@test.com', full_name='Fresh Test', student_id='ST999', role='student')
    db.session.add(u)
    db.session.commit()
    
    login_user(u)
    try:
        print("Rendering Student Portal for fresh student...")
        html = student_portal()
        print("Success, length =", len(html))
    except Exception as e:
        traceback.print_exc(file=sys.stdout)
    finally:
        db.session.delete(u)
        db.session.commit()
