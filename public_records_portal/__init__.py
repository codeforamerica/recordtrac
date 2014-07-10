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

set_env(key = 'APPLICATION_URL', default = "http://127.0.0.1:5000/") 
set_env(key = 'SQLALCHEMY_DATABASE_URI', default = "postgresql://localhost/recordtrac")
set_env(key = 'ENVIRONMENT', default="LOCAL")
# The default records liaison, to whom requests get routed to if no department is selected:
set_env(key = 'DEFAULT_OWNER_EMAIL', default = 'recordtrac@postcode.io')
set_env(key = 'DEFAULT_OWNER_REASON', default = 'Open government coordinator' )

set_env(key = 'HOST_URL', default = 'https://www.scribd.com/doc/') # Where the documents/record uploads are hosted
set_env(key = 'AGENCY_NAME', default = 'Your agency name') # e.g. City of Oakland
set_env(key = 'SECRET_KEY', default = 'Change this to something super secret') # Flask application's secret key

# The number of days an agency has (determined by law or policy) to fulfill a request
set_env(key = 'DAYS_TO_FULFILL', default = '10')
set_env(key = 'DAYS_AFTER_EXTENSION', default = '14')


# Set rest of the variables that don't have defaults:
envvars = [
			'DEFAULT_MAIL_SENDER', # The e-mail address used as the FROM field for all notifications
			'MAIL_USERNAME', # The SendGrid username
			'MAIL_PASSWORD', # The SendGrid password
			'SENDGRID_MONTHLY_LIMIT', # Your SendGrid Monthly Limit
			'LIST_OF_ADMINS', # Defines who has admin access (/admin) with a comma delimited list of e-mail addresses. i.e. 'richa@codeforamerica.org,cris@codeforamerica.org'
			'SECRET_KEY', # Flask app secret key
			'SCRIBD_API_KEY',
			'SCRIBD_API_SECRET',
			'AKISMET_KEY', # Used for spam filtering
			'RECAPTCHA_PUBLIC_KEY',
			'RECAPTCHA_PRIVATE_KEY',
			'DEV_EMAIL', # Used for local e-mail testing if set
			'GOOGLE_FEEDBACK_FORM_ID', # The form ID that the feedback tab is hooked up to,
			'STAFF_FILEPATH', # The path/URL at which a csv containing staff data lives. If this is not set, no one will be able to log into RecordTrac
			'LIAISONS_FILEPATH' # The path/URL at which a csv containing liaisons/department data lives. If this is not set, initial request routing will always be directed to the default owner
			,
			]
for envvar in envvars:
	set_env(key = envvar)


# Initialize database
db = SQLAlchemy(app)

