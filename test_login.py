from app import app
with app.app_context():
    app.config['TESTING'] = True
    client = app.test_client()
    res = client.get('/login')
    print("STATUS:", res.status_code)
    if res.status_code != 200:
        print("ERROR DUMP:")
        print(res.data.decode('utf-8'))
