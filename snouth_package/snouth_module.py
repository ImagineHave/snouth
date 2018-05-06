from flask import Flask, request, jsonify
from flask_mail import Mail, Message
import pymongo
import random
import string
import os
from datetime import datetime
from flask_jwt_extended import JWTManager
from flask_jwt_extended import (create_access_token, create_refresh_token, jwt_required, jwt_refresh_token_required, get_jwt_identity, get_raw_jwt)
import requests

    
app = Flask(__name__)

app.config.update(dict(
    SECRET_KEY = os.environ['SECRET_KEY'],
    MAIL_USERNAME = os.environ['MAIL_USERNAME'],
    MAILGUN_API_KEY = os.environ['MAILGUN_API_KEY'],
    MAILGUN_URL = os.environ['MAILGUN_URL'],
    JWT_SECRET_KEY = os.environ['JWT_SECRET_KEY'],
    MONGO_URI = os.environ['MONGO_URI']
    ))

mail = Mail(app)
jwt = JWTManager(app)

client = pymongo.MongoClient(app.config['MONGO_URI'])
db = client.get_default_database()


@app.route('/userRegistration', methods=['POST'])
def registerUser():
    
    dataDict = request.get_json()
    
    email = dataDict['email']
    password = dataDict['password']
    activationString = generateActivationParameter()
    
    db.users.insert({
        'email': email,
        'password': password,
        'created_time': datetime.utcnow(),
        'activation': activationString        
        })   
        
    send_email(email, activationString)
    
    return ('', 204)

@app.route('/activation', methods=['GET'])
def activateUser():
    email = request.args.get('em','')
    activationToken = request.args.get('at','')
    
    query = {'email': email, 'activation': activationToken}
    
    user = db.users.find_one(query)
    
    print(user)
    
    if not user:
        return ('', 401)
    
    
    db.users.update_one({
        '_id': user['_id']
    },{
        '$set': {
            'activation': True
        }
    }, upsert=False)
    
    return('', 202)
    
@app.route('/userLogon', methods=['POST'])
def login():
    dataDict = request.get_json()
    
    email = dataDict['email']
    password = dataDict['password']
    
    query = {'email': email, 'password': password}
    
    user = db.users.find_one(query)
    
    print(user)
    
    if not user:
        return ('', 401)
    
    identity = {"email":user['email'], "password":user['password']}
    print(identity)
    refreshToken = create_refresh_token(identity)
    
    db.users.update_one({
        '_id': user['_id']
    },{
        '$set': {
            'refreshToken': refreshToken
        }
    }, upsert=False)
    
    return(refreshToken,200) 

@app.route('/refreshExchange', methods=['POST'])
@jwt_refresh_token_required
def getAccessTokenAndRefreshRefreshToken():
    
    print(get_jwt_identity())
    current_user = get_jwt_identity()
    print(current_user)
    access_token = create_access_token(identity = current_user)
    refreshToken = create_refresh_token(identity = current_user)
    
    return jsonify({'access_token': access_token, 'refreshToken':refreshToken})
        
def send_email(email, activationString):
    request_url = '{0}/messages'.format(app.config['MAILGUN_URL'])
    request = requests.post(
        request_url, 
        auth=('api', app.config['MAILGUN_API_KEY']),
        data={'from':app.config['MAIL_USERNAME'], 
        'to':email, 
        'subject':"Hello Activation message sent from Flask-Mail with activation string http://localhost:5000/activation?em="+email+"&at="+activationString, 
        'text': 'Hello there'}
        )
    print(request.status_code)
    print(request.text)
    

def generateActivationParameter():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=255))
	