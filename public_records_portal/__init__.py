# import os 
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy

# Initialize Flask app and database:
app = Flask(__name__)
db = SQLAlchemy(app)
db.create_all()

# Get configuration settings from settings.cfg
# config = os.path.join(app.root_path, 'settings.cfg')
# app.config.from_pyfile(config)
app.config.from_object('websiteconfig')
from public_records_portal import prflask