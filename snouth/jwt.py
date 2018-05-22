from flask_jwt_extended import JWTManager
from flask import current_app, g
from .blacklistaccess import is_refresh_token_in_blacklist

def init_app(app):
    """get JWT Manager"""
    with app.app_context():
        jwtmanager = JWTManager(app)
        
        @jwtmanager.token_in_blacklist_loader
        def check_if_refresh_token_in_blacklist(decrypted_token):
            print ('check refresh token')
            print ('jti to check', decrypted_token['jti'])
            return is_refresh_token_in_blacklist(decrypted_token['jti'])
            
        g.jwtmanager = jwtmanager
        return g.jwtmanager

