"""A flask app to handle public records requests and display responses.

.. moduleauthor:: Richa Agarwal <richa@postcode.io>

"""

import logging
from os import environ
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy

# Initialize Flask app 
app = Flask(__name__)
app.debug = True

# Set environment variables
def set_env(key, default = None):
	if key in environ:
		app.config[key] = environ[key]
	elif default:
		app.config[key] = default

# UPDATES TO THESE DEFAULTS SHOULD OCCUR IN YOUR .env FILE.

# The basics, these should be accurate or the app will not run properly:
set_env(key = 'APPLICATION_URL', default = "http://127.0.0.1:5000/")
set_env(key = 'SQLALCHEMY_DATABASE_URI', default = "postgresql://localhost/recordtrac")
set_env(key = 'ENVIRONMENT', default="LOCAL")
# Set the default records liaison, this matters more in a production environment:
set_env(key = 'DEFAULT_OWNER_EMAIL', default = 'recordtrac@postcode.io')
set_env(key = 'DEFAULT_OWNER_NAME', default = 'PostCode.io')
set_env(key = 'DEFAULT_OWNER_REASON', default = 'PostCode.io can help you get @recordtrac in your agency.' )
# If you set up Sendgrid or another e-mail service:
set_env(key = 'DEFAULT_MAIL_SENDER', default = '')  # The e-mail address used as the FROM field for all notifications
set_env(key = 'MAIL_USERNAME', default='') # The SendGrid username
set_env(key = 'MAIL_PASSWORD', default = '') # The SendGrid password
set_env(key='SENDGRID_MONTHLY_LIMIT', default='') # Your SendGrid Monthly Limit
# User login default, password can be used with any e-mail address:
set_env(key = 'ADMIN_PASSWORD', default = 'admin')
# Define who has admin access (/admin) with a comma delimited list of e-mail addresses:
set_env(key = 'LIST_OF_ADMINS')
# Flask app secret key:
set_env(key = 'SECRET_KEY')
# For Scribd uploads:
set_env(key = 'SCRIBD_API_KEY')
set_env(key = 'SCRIBD_API_SECRET')
set_env(key = 'HOST_URL', default = 'https://www.scribd.com/doc/')
# For spam filtering:
set_env(key = 'AKISMET_KEY')
# For CAPTCHA:
set_env(key = 'RECAPTCHA_PUBLIC_KEY')
set_env(key = 'RECAPTCHA_PRIVATE_KEY')
# The name of your agency, e.g. City of Oakland:
set_env(key = 'AGENCY_NAME', default = 'Your agency name')

# The number of days an agency has (determined by law or policy) to fulfill a request
set_env(key = 'DAYS_TO_FULFILL', default = '10')
set_env(key = 'DAYS_AFTER_EXTENSION', default = '14')

# No defaults should be set for this.  Used for local e-mail testing.
set_env(key = 'DEV_EMAIL')

set_env(key = 'GOOGLE_FEEDBACK_FORM_ID')

# If this is not set, no one will be able to log into RecordTrac
set_env(key = 'STAFF_FILEPATH')

# If this is not set, requests will initially be routed only to the default owner
set_env(key = 'LIAISONS_FILEPATH')


# Initialize database
db = SQLAlchemy(app)

logging.basicConfig()
# logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
