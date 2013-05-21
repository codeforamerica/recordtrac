# import os 
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.heroku import Heroku

# Initialize Flask app and database:
app = Flask(__name__)
db = SQLAlchemy(app)
db.create_all()

app.config.from_object('websiteconfig')
heroku = Heroku(app) 
from public_records_portal import prflask