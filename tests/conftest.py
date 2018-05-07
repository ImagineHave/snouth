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
        'SECRET_KEY' : "secret",
        'MAIL_USERNAME' : "mail username",
        'MAILGUN_API_KEY' : "mail api key",
        'MAILGUN_URL' : "mail url",
        'JWT_SECRET_KEY' : "jwt secret",
        'MONGO_URI' : os.environ['TEST_URI'],
        'DOMAIN' : "domain"
    })
    
    with app.app_context():
        init_db()
        
    yield client
    
@pytest.fixture
def client(app):
    return app.test_client()
    

@pytest.fixture
def runner(app):
    return app.test_cli_runner()