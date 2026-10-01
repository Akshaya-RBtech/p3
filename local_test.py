from app import app, db, User
with app.app_context():
    app.config['TESTING'] = True
    client = app.test_client()
    with client.session_transaction() as sess:
        sess['_user_id'] = '1' # Assuming user 1 is admin
    
    res = client.get('/admin/dashboard')
    print("STATUS:", res.status_code)
    if res.status_code != 200:
        print("ERROR DUMP:")
        print(res.data.decode('utf-8'))
