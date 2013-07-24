"""A flask app to handle public records requests and display responses.

.. moduleauthor:: Richa Agarwal <richa@codeforamerica.org>

"""

from os import environ
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.restless import APIManager
import flask.ext.restless

# Initialize Flask app and database:
app = Flask(__name__)
app.debug = True

def set_env(key, default):
	if key in environ:
		app.config[key] = environ[key]
	else:
		app.config[key] = default

# You can set these in a file such as settings.env. See settings.env.example

set_env(key = 'ENVIRONMENT', default="LOCAL")

set_env(key = 'DEFAULT_OWNER_REASON', default = 'The reason the default owner gets assigned a request' )
set_env(key = 'DEFAULT_OWNER_EMAIL', default = 'citystaff@city.gov')
# If you set up Sendgrid...
set_env(key = 'DEFAULT_MAIL_SENDER', default = 'appemail@app.com') 
set_env(key = 'MAIL_USERNAME', default='Oakland Public Records')
set_env(key = 'MAIL_PASSWORD', default = "")

# For app logins
set_env(key = 'ADMIN_PASSWORD', default = "NotSoSecretPassword")

# Flask app secret key
set_env(key = 'SECRET_KEY', default = "NotSoSecretKey")

set_env(key = 'APPLICATION_URL', default = "http://127.0.0.1:5000/")

# For Scribd uploads...
set_env(key = 'SCRIBD_API_KEY', default = "")
set_env(key = 'SCRIBD_API_SECRET', default = "")

set_env(key = 'SQLALCHEMY_DATABASE_URI', default = "postgresql://localhost/publicrecords")
set_env(key = 'HOST_URL', default = 'https://www.scribd.com/doc/')


db = SQLAlchemy(app)
from public_records_portal import models
from models import *

# Create API
# Maybe move this over to prflask and comment on how this sets up the URLs
manager = APIManager(app, flask_sqlalchemy_db=db)
manager.create_api(Request, methods=['GET', 'POST', 'PUT', 'DELETE'], results_per_page=None)
manager.create_api(Owner, methods=['GET', 'POST', 'PUT', 'DELETE'], results_per_page = None)
manager.create_api(Note, methods=['GET', 'POST', 'PUT', 'DELETE'], results_per_page = None)
manager.create_api(Record, methods=['GET', 'POST', 'PUT', 'DELETE'], results_per_page = None)
manager.create_api(QA, methods=['GET', 'POST', 'PUT', 'DELETE'], results_per_page =None)
manager.create_api(Subscriber, methods=['GET', 'POST', 'PUT', 'DELETE'], results_per_page = None)