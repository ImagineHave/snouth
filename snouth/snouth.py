from flask import Blueprint, request, current_app, request, jsonify
from .useraccess import find_user_by_email_and_activation, activate_user, create_user, find_user_by_email_and_password, set_user_refreshtoken
from .blacklistaccess import insert_blacklist
import requests
import random
import string
from flask_jwt_extended import (create_access_token, create_refresh_token, jwt_required, jwt_refresh_token_required, get_jwt_identity, get_raw_jwt)

bp = Blueprint('snouth', __name__, url_prefix='/snouth')

def generateActivationParameter():
    return ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(255))


def send_activation_email(email, activationString):
    request_url = '{0}/messages'.format(current_app.config['MAILGUN_URL'])
    response = requests.post(
        request_url, 
        auth=('api', current_app.config['MAILGUN_API_KEY']),
        data={'from':current_app.config['MAIL_USERNAME'], 
        'to':email, 
        'subject':"Activation link", 
        'text': 'https://'+current_app.config['DOMAIN']+'/snouth/activation?em='+email+'&at='+activationString}
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
    
    activation_string = generateActivationParameter()
    
    create_user(email, password, activation_string)
   
    send_activation_email(email, activation_string)
    
    return ('', 204)
    
@bp.route('/activation', methods=['GET'])
def activateUser():
    email = request.args.get('em','')
    activation = request.args.get('at','')
    
    print(email)
    print(activation)
    
    user = find_user_by_email_and_activation(email, activation)
    
    print(user)
    
    if not user:
        return ('', 401)
    
    activate_user(user)
    
    return('', 202)
    

@bp.route('/userLogon', methods=['POST'])
def login():
    dataDict = request.get_json()
    email = dataDict['email']
    password = dataDict['password']
    
    user = find_user_by_email_and_password(email, password)
    
    print(user)
    
    if not user:
        return ('', 401)
    
    identity = {"email":user['email'], "password":user['password']}
    print(identity)
    print(user)
    refreshToken = create_refresh_token(identity)
    
    set_user_refreshtoken(user, refreshToken)
    
    return jsonify({'refreshToken': refreshToken})
    
@bp.route('/refreshExchange', methods=['POST'])
@jwt_refresh_token_required
def getAccessTokenAndRefreshRefreshToken():
    
    print('jwt identity ',get_jwt_identity())
    current_user = get_jwt_identity()
    print('current user', current_user)
    accessToken = create_access_token(identity = current_user)
    refreshToken = create_refresh_token(identity = current_user)
    
    return jsonify({'accessToken': accessToken, 'refreshToken':refreshToken})
    
@bp.route('/blacklist', methods=['POST'])
@jwt_refresh_token_required
def blacklistRefreshToken():
    jti = get_raw_jwt()['jti']
    print ('jti ', jti)
    insert_blacklist(jti)
    return ('', 200)