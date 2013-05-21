from os import environ
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.heroku import Heroku

# Initialize Flask app and database:
app = Flask(__name__)
app.config.from_object('websiteconfig')
db = SQLAlchemy(app)
db.create_all()
 
from public_records_portal import prflask