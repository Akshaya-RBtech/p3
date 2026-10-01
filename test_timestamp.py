from app import app, db, User, Vote
from datetime import datetime
with app.app_context():
    app.config['TESTING'] = True
    
    # insert a bad vote just in case
    if not Vote.query.first():
        v = Vote(student_id='ST001', menu_id=1, choice='No', reason='Test', timestamp=None)
        db.session.add(v)
        db.session.commit()
    
    client = app.test_client()
    with client.session_transaction() as sess:
        sess['_user_id'] = '1'
    
    res = client.get('/admin/dashboard')
    print("STATUS:", res.status_code)
    if res.status_code != 200:
        print("ERROR:", res.data.decode('utf-8')[:500])
