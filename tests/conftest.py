# -*- coding: utf-8 -*-
"""
    Snouth Tests
    ~~~~~~~~~~~~
    Tests the Snouth application.
    :copyright: (c) 2018 by Imagine-have.
    :license: BSD, see LICENSE for more details.
"""

import os
import tempfile
import pytest
from snouth import create_app
from snouth.db import get_db, init_db
from pymongo import MongoClient

@pytest.fixture
def app():
    
    app = create_app({
        'TESTING': True,
        'SECRET_KEY' : os.environ['SECRET_KEY'],
        'MAIL_USERNAME' : os.environ['MAIL_USERNAME'],
        'MAILGUN_API_KEY' : os.environ['MAILGUN_API_KEY'],
        'MAILGUN_URL' : os.environ['MAILGUN_URL'],
        'JWT_SECRET_KEY' : os.environ['JWT_SECRET_KEY'],
        'MONGO_URI' : os.environ['MONGO_URI'],
        'DOMAIN' : os.environ['DOMAIN']
    })
    
    with app.app_context():
        init_db()
        
    yield app
    
@pytest.fixture
def client(app):
    return app.test_client()
    

@pytest.fixture
def runner(app):
    return app.test_cli_runner()