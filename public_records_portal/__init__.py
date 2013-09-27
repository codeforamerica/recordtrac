"""A flask app to handle public records requests and display responses.

.. moduleauthor:: Richa Agarwal <richa@codeforamerica.org>

"""

from os import environ
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy

# Initialize Flask app 
app = Flask(__name__)
app.debug = True

# Set environment variables
def set_env(key, default):
	if key in environ:
		app.config[key] = environ[key]
	else:
		app.config[key] = default

# You can overwrite these defaults, ideally in a file such as settings.env. See settings.env.example
set_env(key = 'APPLICATION_URL', default = "http://127.0.0.1:5000/")
set_env(key = 'ENVIRONMENT', default="LOCAL")
set_env(key = 'DEFAULT_OWNER_REASON', default = 'The reason the default owner gets assigned a request' )
set_env(key = 'DEFAULT_OWNER_EMAIL', default = 'citystaff@city.gov')
set_env(key = 'SQLALCHEMY_DATABASE_URI', default = "postgresql://localhost/publicrecords")
# If you set up Sendgrid or another e-mail service:
set_env(key = 'DEFAULT_MAIL_SENDER', default = 'appemail@app.com') 
set_env(key = 'MAIL_USERNAME', default='Oakland Public Records')
set_env(key = 'MAIL_PASSWORD', default = "")
# For app logins
set_env(key = 'ADMIN_PASSWORD', default = "NotSoSecretPassword")
# Flask app secret key
set_env(key = 'SECRET_KEY', default = "NotSoSecretKey")
# For Scribd uploads...
set_env(key = 'SCRIBD_API_KEY', default = "")
set_env(key = 'SCRIBD_API_SECRET', default = "")
set_env(key = 'HOST_URL', default = 'https://www.scribd.com/doc/')
set_env(key = 'AKISMET_KEY', default = "")

# Initialize database
db = SQLAlchemy(app)
