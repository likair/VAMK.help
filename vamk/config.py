# -*- coding: utf-8 -*-
"""
    vamk.config
    ~~~~~~~~~~~
    Implements the configuration of the application.

    :copyright: (c) 2016 by Likai Ren.
    :license: BSD, see LICENSE for more details.
"""

from authomatic.providers import oauth2

# Configuration of Authomatic.
CONFIG = {
    'fb': {
        'class_': oauth2.Facebook,
        # Replacing stars to Facebook APP ID.
        'consumer_key': '******************',
        # Replacing stars to Facebook APP secret.
        'consumer_secret': '******************',
        'scope': [],
    }
}
# Configuration of Flask-SQLAlchemy.
# Replacing stars to Database URI.
SQLALCHEMY_DATABASE_URI = '******************'
SQLALCHEMY_TRACK_MODIFICATIONS = True
# Configuration of Flask.
# Replacing stars to the customized secret key.
SECRET_KEY = '******************'
# DEBUG = True
PORT = 8000
HOST='127.0.0.1'
THREADED = True
