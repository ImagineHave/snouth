from flask import Flask, request
from flask_mail import Mail, Message
import pymongo
import random
import string
from datetime import datetime


app = Flask(__name__)

app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'activation@imagine-have.xyz'
app.config['MAIL_PASSWORD'] = ''
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)


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
    


def send_email(email, activationString):
    msg = Message('Hello', sender = 'activation@imagine-have.xyz', recipients = [email])
    msg.body = "Hello Activation message sent from Flask-Mail with activation string http://localhost:5000/activation?em="+email+"&at="+activationString
    mail.send(msg)

def generateActivationParameter():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=255))
	