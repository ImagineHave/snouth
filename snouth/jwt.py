from flask_jwt_extended import JWTManager
from flask import current_app, g
from .useraccess import find_user_by_email_and_password

def init_app(app):
    """get JWT Manager"""
    with app.app_context():
        jwtmanager = JWTManager(app)
        
        @jwtmanager.token_in_blacklist_loader
        def check_if_refresh_token_in_blacklist(decrypted_token):
            print ('jti to check', decrypted_token['jti'])
            print (decrypted_token)
            
            identity = decrypted_token['identity']
            user = find_user_by_email_and_password(identity['email'],identity['password'])
            
            print (user)
            return user != None and user['refreshToken'] != decrypted_token['jti']
            
        g.jwtmanager = jwtmanager
        return g.jwtmanager

