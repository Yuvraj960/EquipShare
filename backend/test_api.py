import os
os.environ['PYTHONPATH'] = '.'
from app import create_app
app = create_app()
client = app.test_client()
data = {'email':'test3@test.com','username':'testuser3','password':'pass123'}
resp = client.post('/api/auth/register', json=data)
print(resp.status_code)
print(resp.get_data(as_text=True))
