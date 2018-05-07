from .db import get_db
from flask import Blueprint, g, request, current_app, request, jsonify
from datetime import datetime
from werkzeug.security import check_password_hash, generate_password_hash
import requests
import random
import string
from flask_jwt_extended import (create_access_token, create_refresh_token, jwt_required, jwt_refresh_token_required, get_jwt_identity, get_raw_jwt)

bp = Blueprint('snouth', __name__, url_prefix='/snouth')


def generateActivationParameter():
    return ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(255))


def send_email(email, activationString):
    request_url = '{0}/messages'.format(current_app.config['MAILGUN_URL'])
    response = requests.post(
        request_url, 
        auth=('api', current_app.config['MAILGUN_API_KEY']),
        data={'from':current_app.config['MAIL_USERNAME'], 
        'to':email, 
        'subject':"Hello Activation message sent from Flask-Mail with activation string https://"+current_app.config['DOMAIN']+"/snouth/activation?em="+email+"&at="+activationString, 
        'text': 'Hello there'}
        )
    print("----")
    print("send mail response:")
    print(response.status_code)
    print(response.text)
    print("----")
    

@bp.route('/userRegistration', methods=['POST'])
def registerUser():
    
    dataDict = request.get_json()
    email = dataDict['email']
    password = dataDict['password']
    db = get_db()
    
    activationString = generateActivationParameter()
    
    db.users.insert({
        'email': email,
        'password': password,
        'created_time': datetime.utcnow(),
        'activation': activationString        
        })   
        
    send_email(email, activationString)
    
    return ('', 204)
    
@bp.route('/activation', methods=['GET'])
def activateUser():
    email = request.args.get('em','')
    activationToken = request.args.get('at','')
    db = get_db()
    
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
    

@bp.route('/userLogon', methods=['POST'])
def login():
    dataDict = request.get_json()
    email = dataDict['email']
    password = dataDict['password']
    
    query = {'email': email, 'password': password}
    
    db = get_db()
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
    
@bp.route('/refreshExchange', methods=['POST'])
@jwt_refresh_token_required
def getAccessTokenAndRefreshRefreshToken():
    
    print(get_jwt_identity())
    current_user = get_jwt_identity()
    print(current_user)
    access_token = create_access_token(identity = current_user)
    refreshToken = create_refresh_token(identity = current_user)
    
    return jsonify({'access_token': access_token, 'refreshToken':refreshToken})