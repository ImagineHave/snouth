from flask import Flask, request, jsonify
from flask_mail import Mail, Message
import pymongo
import random
import string
import os
from datetime import datetime
from flask_jwt_extended import JWTManager
from flask_jwt_extended import (create_access_token, create_refresh_token, jwt_required, jwt_refresh_token_required, get_jwt_identity, get_raw_jwt)

    
snouth_instance = Flask(__name__)

snouth_instance.config['MAIL_SERVER']=os.environ['MAIL_SERVER']
snouth_instance.config['MAIL_PORT'] = os.environ['MAIL_PORT']
snouth_instance.config['MAIL_USERNAME'] = os.environ['MAIL_USERNAME']
snouth_instance.config['MAIL_PASSWORD'] = os.environ['MAIL_PASSWORD']
snouth_instance.config['MAIL_USE_TLS'] = os.environ['MAIL_USE_TLS']
snouth_instance.config['MAIL_USE_SSL'] = os.environ['MAIL_USE_SSL']

mail = Mail(snouth_instance)

snouth_instance.config['JWT_SECRET_KEY'] = os.environ['JWT_SECRET_KEY']

jwt = JWTManager(snouth_instance)

uri = os.environ['MONGO_URI']
client = pymongo.MongoClient(uri)
db = client.get_default_database()

@snouth_instance.route('/userRegistration', methods=['POST'])
def registerUser():
    dataDict = request.get_json()
    
    email = dataDict['email']
    password = dataDict['password']
    print(email)
    print(password)
    activationString = generateActivationParameter()
    print(activationString)
    
    db.users.insert({
        'email': email,
        'password': password,
        'created_time': datetime.utcnow(),
        'activation': activationString        
        })     
        
    send_email(email, activationString)
    
    return ('', 204)

@snouth_instance.route('/activation', methods=['GET'])
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
    
@snouth_instance.route('/userLogon', methods=['POST'])
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

@snouth_instance.route('/refreshExchange', methods=['POST'])
@jwt_refresh_token_required
def getAccessTokenAndRefreshRefreshToken():
    
    print(get_jwt_identity())
    current_user = get_jwt_identity()
    print(current_user)
    access_token = create_access_token(identity = current_user)
    refreshToken = create_refresh_token(identity = current_user)
    
    return jsonify({'access_token': access_token, 'refreshToken':refreshToken})
    
    
def send_email(email, activationString):
    msg = Message('Hello', sender = 'postmaster@sandbox24975759833748b691661a5098f12fdb.mailgun.org', recipients = [email])
    msg.body = "Hello Activation message sent from Flask-Mail with activation string http://localhost:5000/activation?em="+email+"&at="+activationString
    mail.send(msg)

def generateActivationParameter():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=255))
	