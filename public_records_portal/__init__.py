from os import environ
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy

# Initialize Flask app and database:
app = Flask(__name__)
try:
	app.config.from_object('local_config')
except:
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
	app.config['SECRET_KEY'] = environ['SECRET_KEY']
	app.config['SQLALCHEMY_DATABASE_URI'] = environ['SQLALCHEMY_DATABASE_URI']

db = SQLAlchemy(app)
db.create_all()
 
from public_records_portal import prflask