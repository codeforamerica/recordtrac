from os import environ
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.heroku import Heroku

# Initialize Flask app and database:
app = Flask(__name__)
try:
	app.config.from_object('local_config')
except:
	heroku = Heroku(app) # Sets app.config from Heroku variables, that should be set already.
db = SQLAlchemy(app)
db.create_all()
 
from public_records_portal import prflask