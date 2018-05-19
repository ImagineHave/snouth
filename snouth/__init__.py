import os

from flask import Flask

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    
    if test_config is None:
        app.config.update(dict(
            SECRET_KEY = os.environ['SECRET_KEY'],
            MAIL_USERNAME = os.environ['MAIL_USERNAME'],
            MAILGUN_API_KEY = os.environ['MAILGUN_API_KEY'],
            MAILGUN_URL = os.environ['MAILGUN_URL'],
            JWT_SECRET_KEY = os.environ['JWT_SECRET_KEY'],
            JWT_BLACKLIST_ENABLED = True,
            JWT_BLACKLIST_TOKEN_CHECKS = ['refresh'],
            MONGO_URI = os.environ['MONGO_URI'],
            DOMAIN = os.environ['DOMAIN']
            ))
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

        
    # a simple page that says hello
    @app.route('/hello')
    def hello():
        return 'Hello, World!'
        
    # register the database commands on the app
    # we can initialise the database
    # database connections get torn down after each request
    from . import db
    db.init_app(app)
    
    from . import snouth
    app.register_blueprint(snouth.bp)
    
    from . import jwt
    jwt.init_app(app)
    
    return app