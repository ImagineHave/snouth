from flask_jwt_extended import JWTManager
from flask import current_app, g

def init_app(app):
    """get JWT Manager"""
    with app.app_context():
        g.jwtmanager = JWTManager(app)
        return g.jwtmanager