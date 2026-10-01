import sys
import traceback
from app import app, student_portal
from flask_login import login_user
from models import User

app.config['TESTING'] = True
with app.test_request_context('/student/portal'):
    u = User.query.filter_by(role='student').first()
    if u:
        login_user(u)
        try:
            print("Rendering Student Portal...")
            html = student_portal()
            print("Success, length =", len(html))
        except Exception as e:
            traceback.print_exc(file=sys.stdout)
    else:
        print("No student user found")
