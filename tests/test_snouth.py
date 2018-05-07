from snouth import create_app
from flask import json
import requests

def registerUser(client, email, password):
    return client.post('/snouth/userRegistration', data=json.dumps(dict(email=email,password=password)), content_type='application/json')

def checkMailgun(app):
    print("hello")
    with app.app_context():
        request_url = '{0}/messages'.format(app.config['MAILGUN_URL'])
        request = requests.get(request_url, auth=('api', app.config['MAILGUN_API_KEY']), params={'limit': 1})
        print(app.config['MAILGUN_URL'])
        print('Status: {0}'.format(request.status_code))
        print('Body:   {0}'.format(request.text))

def test_registerUser(client,app):
    print("hello")
    response = registerUser(client, 'activation@imagine-have.xyz', 'password')
    checkMailgun(app)
    assert response.status_code == 204
    
    