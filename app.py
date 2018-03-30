from flask import Flask, request, jsonify
from flask_mail import Mail, Message
import pymongo
import random
import string
from datetime import datetime
from flask_jwt_extended import JWTManager
from flask_jwt_extended import (create_access_token, create_refresh_token, jwt_required, jwt_refresh_token_required, get_jwt_identity, get_raw_jwt)


app = Flask(__name__)

app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'activation@imagine-have.xyz'
app.config['MAIL_PASSWORD'] = 'HwyShrotalot2016'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)

app.config['JWT_SECRET_KEY'] = 'jwt-secret-string'

jwt = JWTManager(app)

uri = 'mongodb://gateway:gateway4ih@ds227168.mlab.com:27168/userdb'
client = pymongo.MongoClient(uri)
db = client.get_default_database()

@app.route('/userRegistration', methods=['POST'])
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
    msg = Message('Hello', sender = 'activation@imagine-have.xyz', recipients = [email])
    msg.body = "Hello Activation message sent from Flask-Mail with activation string http://localhost:5000/activation?em="+email+"&at="+activationString
    mail.send(msg)

def generateActivationParameter():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=255))
	
    
def authenticate(username, password):
    user = db.users.find_one({"email":username})
    if user and user['password'] == password:
        return user

def identity(payload):
    user_id = payload['identity']    
    return db.users.find_one({"email":user_id})