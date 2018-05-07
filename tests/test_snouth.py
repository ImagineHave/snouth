from snouth import create_app
from flask import json

def registerUser(client, email, password):
    return client.post('/snouth/userRegistration', data=json.dumps(dict(email=email,password=password)), content_type='application/json')

def test_registerUser(client):
    response = registerUser(client, 'em@ai.l', 'password')
    assert response.data == b'Hello, World!'