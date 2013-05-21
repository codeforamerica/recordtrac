from os import environ
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy

# Initialize Flask app and database:
app = Flask(__name__)
try:
	app.config.from_object('local_config')
except:
	pass # TODO: better way to set heroku config
db = SQLAlchemy(app)
db.create_all()
 
from public_records_portal import prflask