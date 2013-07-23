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
app.config['SECRET_KEY'] = "Not really a secret."
app.config['ENVIRONMENT'] = "LOCAL"
app.config['DEFAULT_OWNER_REASON'] = "Default owner reason"
app.config['DEFAULT_OWNER_EMAIL'] = "Default owner email"

app.config.from_object(environ)
if app.config['ENVIRONMENT'] == 'LOCAL':
	app.config.from_object('local_config')

db = SQLAlchemy(app)
from public_records_portal import models
from models import *

# Create API
manager = APIManager(app, flask_sqlalchemy_db=db)
manager.create_api(Request, methods=['GET', 'POST', 'PUT', 'DELETE'], results_per_page=None)
manager.create_api(Owner, methods=['GET', 'POST', 'PUT', 'DELETE'], results_per_page = None)
manager.create_api(Note, methods=['GET', 'POST', 'PUT', 'DELETE'], results_per_page = None)
manager.create_api(Record, methods=['GET', 'POST', 'PUT', 'DELETE'], results_per_page = None)
manager.create_api(QA, methods=['GET', 'POST', 'PUT', 'DELETE'], results_per_page =None)
manager.create_api(Subscriber, methods=['GET', 'POST', 'PUT', 'DELETE'], results_per_page = None)