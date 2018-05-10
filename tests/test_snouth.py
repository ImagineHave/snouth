from snouth import create_app
from snouth.db import get_db
from flask import json
import time
from datetime import datetime
import requests

def activation(client, app, email, activation):
    with app.app_context():
        print('activation')
        return client.get('https://'+app.config['DOMAIN']+'/snouth/activation?em='+email+'&at='+activation)

def registerUser(client, email, password):
    return client.post('/snouth/userRegistration', data=json.dumps(dict(email=email, password=password)), content_type='application/json')
    
def userLogon(client, email, password):
    return client.post('/snouth/userLogon', data=json.dumps(dict(email=email, password=password)), content_type='application/json')

def refreshExchange(client, refreshToken):
    headers = {'Authorization': 'Bearer ' + refreshToken, 'content_type':'application/json'}
    return client.post('/snouth/refreshExchange', data=json.dumps(dict(refreshToken=refreshToken)), headers= headers)

def convertDateTime(ts):
    return datetime.fromtimestamp(ts)

def checkMailgun(app):
    with app.app_context():
        request_url = '{0}/events'.format(app.config['MAILGUN_URL'])
        response = requests.get(request_url, auth=('api', app.config['MAILGUN_API_KEY']), params={'limit':'1'})
        return convertDateTime(response.json()['items'][0]['timestamp'])
        
def test_registerUser(client,app):
    appResponse = registerUser(client, 'activation@imagine-have.xyz', 'password')
    sendTime = convertDateTime(time.time())
    emailTimeStamp = checkMailgun(app)
    print(appResponse.status_code)
    print(emailTimeStamp)
    print(sendTime)
    print((emailTimeStamp - sendTime).total_seconds())
    assert appResponse.status_code == 204
    assert (emailTimeStamp - sendTime).total_seconds() <= 20

def test_activation(client, app):
    
    email = 'activation@imagine-have.xyz'
    password = 'password'
    activationString = 'gobbleDeeGook'
    
    # register
    with app.app_context():
        db = get_db()
        db.users.insert({
        'email': email,
        'password': password,
        'created_time': datetime.utcnow(),
        'activation': activationString        
        }) 
        
        activation(client, app, email, activationString)

        query = {'email': email, 'activation': True}
        user = db.users.find_one(query)
        print(user)
        assert user['activation'] == True
        
def test_userLogon(client, app):
    email = 'activation@imagine-have.xyz'
    password = 'password'
    activated = True
    
    # register
    with app.app_context():
        db = get_db()
        db.users.insert({
        'email': email,
        'password': password,
        'activation': activated        
        }) 
        
        appResponse = userLogon(client, email, password)
        jsonResponse = json.loads(appResponse.get_data(as_text=True))
        print (jsonResponse)
        
        assert appResponse.status_code == 200
        assert len(jsonResponse['refreshToken']) > 0

def test_refreshExchange(client, app):
    refreshToken = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpYXQiOjE1MjQyNDkxMTMsIm5iZiI6MTUyNDI0OTExMywianRpIjoiMjBiMTNhNzMtY2ZhMy00Y2E1LTlhZGItMzkzZmJkYmIzMDVmIiwiZXhwIjoxNTI2ODQxMTEzLCJpZGVudGl0eSI6eyJlbWFpbCI6Im95dmluZC53b2xsZXJAaW1hZ2luZS1oYXZlLnh5eiIsInBhc3N3b3JkIjoieDRkc2QyZHM0In0sInR5cGUiOiJyZWZyZXNoIn0.KsXQ0HabM8uLoKX5GYDPh6GdDeTf3HFVgUIKMR03VaE"
    appResponse = refreshExchange(client, refreshToken)
    jsonResponse = json.loads(appResponse.get_data(as_text=True))
    assert appResponse.status_code == 200
    assert len(jsonResponse['refreshToken']) > 0
    assert len(jsonResponse['accessToken']) > 0