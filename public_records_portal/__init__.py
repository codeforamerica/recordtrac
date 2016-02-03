"""A flask app to handle public records requests and display responses.

	Initializes application and all of its environment variables.

.. moduleauthor:: Richa Agarwal <richa@codeforamerica.org>

"""

import logging
from os import environ
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.babel import Babel

# Initialize Flask app
app = Flask(__name__)
app.debug = True

# Set environment variables
def set_env(key, default = None):
	if key in environ:
		app.config[key] = environ[key]
	elif default:
		app.config[key] = default

def set_bool_env(key, default = None):
	if key in environ:
		app.config[key] = environ[key].lower() in ('true', 'yes', 'on')
	elif default is not None:
		app.config[key] = default

# UPDATES TO THESE DEFAULTS SHOULD OCCUR IN YOUR .env FILE.

set_env(key = 'APPLICATION_URL', default = "http://127.0.0.1:5000/")
set_env(key = 'ENVIRONMENT', default="LOCAL")
# The default records liaison, to whom requests get routed to if no department is selected:
set_env(key = 'DEFAULT_OWNER_EMAIL', default = 'recordtrac@codeforamerica.org')
set_env(key = 'DEFAULT_OWNER_REASON', default = 'Open government coordinator' )

set_env(key = 'AGENCY_NAME', default = 'Your agency name') # e.g. City of Oakland
set_env(key = 'SECRET_KEY', default = 'Change this to something super secret') # Flask application's secret key

# The number of days an agency has (determined by law or policy) to fulfill a request
# Currently due dates and overdue status is only showed to logged in agency staff
set_env(key = 'DAYS_TO_FULFILL', default = '10')
set_env(key = 'DAYS_AFTER_EXTENSION', default = '14')
set_env(key = 'DAYS_UNTIL_OVERDUE', default = '2')

set_env(key = 'TIMEZONE', default = "US/Pacific")
set_env(key = 'BABEL_DEFAULT_LOCALE', default = "en")
set_env(key = 'BABEL_DEFAULT_TIMEZONE', default = "US/Pacific")

# Set rest of the variables that don't have defaults:
envvars = [
			'DEFAULT_MAIL_SENDER', # The e-mail address used as the FROM field for all notifications
			'MAIL_USERNAME', # The SendGrid username
			'MAIL_PASSWORD', # The SendGrid password
			'SENDGRID_MONTHLY_LIMIT', # Your SendGrid Monthly Limit
			'LIST_OF_ADMINS', # Defines who has admin access (/admin) with a comma delimited list of e-mail addresses. i.e. 'richa@codeforamerica.org,cris@codeforamerica.org'
			'SECRET_KEY', # Flask app secret key
			'AKISMET_KEY', # Used for spam filtering
			'RECAPTCHA_PUBLIC_KEY',
			'RECAPTCHA_PRIVATE_KEY',
			'DEV_EMAIL', # Used for local e-mail testing if set
			'CHECK_FOR_SPAM', # Used to test spam locally if set
			'GOOGLE_FEEDBACK_FORM_ID', # The form ID that the feedback tab is hooked up to,
			'STAFF_URL', # The path/URL at which a csv containing staff data lives. If this is not set, no one will be able to log into RecordTrac
			'LIAISONS_URL', # The path/URL at which a csv containing liaisons/department data lives. If this is not set, initial request routing will always be directed to the default owner
			'LOGO_ON_WHITE_URL', # The path/URL at which a logo (on a white background) of the agency is hosted. (.png or .jpg)
			'LOGO_ON_BLACK_URL', # The path/URL at which a logo (on a black background) of the agency is hosted. (.png or .jpg)
			'TESTING', # Set if you are running tests. Primarily used to ignore @login_requireds when running tests.
			'SHOULD_UPLOAD' # Set if you want to test uploading documents to the specified host
			]
for envvar in envvars:
	set_env(key = envvar)

# Database gets set slightly differently, to support difference between Flask and Heroku naming:
app.config['SQLALCHEMY_DATABASE_URI'] = environ['DATABASE_URL']

# Initialize database
db = SQLAlchemy(app)

babel = Babel(app)
