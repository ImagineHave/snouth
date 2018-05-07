from flask_jwt_extended import JWTManager
from flask import current_app, g

def init_app(app):
    """get JWT Manager"""
    if not hasattr(g, 'jwtmanager'):
        g.jwtmanager = JWTManager(app)
    return g.jwtmanager