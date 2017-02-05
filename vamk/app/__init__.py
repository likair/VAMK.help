# -*- coding: utf-8 -*-
"""
    vamk.app.__init__
    ~~~~~~~~~~~~~~~~~
    Implements some initializations.

    :copyright: (c) 2016 by Likai Ren.
    :license: BSD, see LICENSE for more details.
"""

from authomatic import Authomatic
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from vamk.config import CONFIG

app = Flask(__name__)
app.config.from_object('config')

# Setting the secret key of the application.
app.secret_key = app.config['SECRET_KEY']

# Instantiating Authomatic.
authomatic = Authomatic(CONFIG, 'your secret string', report_errors=True)

# Instantiating SQLAlchemy.
db = SQLAlchemy(app)
db.create_all()

# Importing the view module after the application object is created.
import views
