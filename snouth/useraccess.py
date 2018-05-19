from .db import get_db
from datetime import datetime


def find_user_by_email_and_activation(email, activation_string):
    db = get_db()
    query = {'email': email, 'activation': activation_string}
    return db.users.find_one(query)

def activate_user(user):
    db = get_db()
    db.users.update_one({
        '_id': user['_id']
    },{
        '$set': {
            'activation': True
        }
    }, upsert=False)
    
def create_user(email, password, activation_string):
    db = get_db()
    
    db.users.insert({
        'email': email,
        'password': password,
        'created_time': datetime.utcnow(),
        'activationString': activation_string        
        })  
        
def find_user_by_email_and_password(email, password):
    query = {'email': email, 'password': password}
    
    db = get_db()
    return db.users.find_one(query)
    
def set_user_refreshtoken(user, refreshToken):
    db = get_db()
    
    db.users.update_one({
        '_id': user['_id']
    },{
        '$set': {
            'refreshToken': refreshToken
        }
    }, upsert=False)
    