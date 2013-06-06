from os import environ
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.restless import APIManager
import flask.ext.restless

# Initialize Flask app and database:
app = Flask(__name__)
app.debug = True
app.config['SECRET_KEY'] = "Not really a secret."
app.config['ENVIRONMENT'] = "LOCAL"
app.config['DEFAULT_OWNER_NAME'] = "Default owner name"
app.config['DEFAULT_OWNER_REASON'] = "Default owner reason"
app.config['DEFAULT_OWNER_EMAIL'] = "Default owner email"

try:
	app.config.from_object('local_config')
except:
	try:
		app.config['SECRET_KEY'] = environ['SECRET_KEY']
		app.config['ENVIRONMENT'] = environ['ENVIRONMENT']
		app.config['APPLICATION_URL'] = environ['APPLICATION_URL']
		app.config['SCRIBD_API_KEY'] = environ['SCRIBD_API_KEY']
		app.config['SCRIPT_API_SECRET'] = environ['SCRIBD_API_SECRET']
		app.config['DEFAULT_OWNER_NAME'] = environ['DEFAULT_OWNER_NAME']
		app.config['DEFAULT_OWNER_EMAIL'] = environ['DEFAULT_OWNER_EMAIL']
		app.config['DEFAULT_OWNER_REASON'] = environ['DEFAULT_OWNER_REASON']
		app.config['MAIL_USERNAME'] = environ['MAIL_USERNAME']
		app.config['MAIL_PASSWORD'] = environ['MAIL_PASSWORD']
		app.config['DEFAULT_MAIL_SENDER'] = environ['DEFAULT_MAIL_SENDER']
		app.config['HOST_URL'] = environ['HOST_URL']
		app.config['SQLALCHEMY_DATABASE_URI'] = environ['SQLALCHEMY_DATABASE_URI']
	except:
		print "Config variables were not set"

db = SQLAlchemy(app)
from public_records_portal import models
from models import *

# Create API
manager = APIManager(app, flask_sqlalchemy_db=db)
manager.create_api(Request, methods=['GET', 'POST', 'PUT', 'DELETE'], results_per_page=None)
manager.create_api(Owner, methods=['GET', 'POST', 'PUT', 'DELETE'])
manager.create_api(Note, methods=['GET', 'POST', 'PUT', 'DELETE'])
manager.create_api(Record, methods=['GET', 'POST', 'PUT', 'DELETE'])
manager.create_api(Note, methods=['GET', 'POST', 'PUT', 'DELETE'])
manager.create_api(QA, methods=['GET', 'POST', 'PUT', 'DELETE'])
manager.create_api(Subscriber, methods=['GET', 'POST', 'PUT', 'DELETE'])