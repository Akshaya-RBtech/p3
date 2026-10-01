import sys
import traceback
from app import app, admin_dashboard
from flask_login import login_user
from models import User

app.config['TESTING'] = True
with app.test_request_context('/admin/dashboard'):
    u = User.query.filter_by(role='admin').first()
    if u:
        login_user(u)
        try:
            print("Rendering Admin Dashboard...")
            html = admin_dashboard()
            print("Success, length =", len(html))
        except Exception as e:
            traceback.print_exc(file=sys.stdout)
    else:
        print("No admin user found")
