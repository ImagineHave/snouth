import os

from django.core.wsgi import get_wsgi_application

WSGI_APPLICATION = 'app.wsgi.application'

application = get_wsgi_application()