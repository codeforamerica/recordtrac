"""
A flask app to handle public records requests and display responses.

Initializes application and all of its environment variables.

.. moduleauthor:: Richa Agarwal <richa@codeforamerica.org>

"""

from os import environ, pardir
from os.path import abspath, dirname, join

from flask import Flask
from flask_recaptcha import ReCaptcha
from flask.ext.sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import pytz
from tzlocal import get_localzone



# Initialize Flask app
app = Flask(__name__)
app.debug = True

load_dotenv(abspath(join(join(dirname(__file__), pardir), '.env')))

# LDAP Settings
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
#app.config['WTF_CSRF_SECRET_KEY'] = 'random key for form'
app.config['LDAP_PROVIDER_URL'] = 'ldaps://ldaps-dev.nycid.nycnet:636/'
# Tester code
def test_Ldap():
    conn = ldap.initialize('ldaps://ldaps-dev.nycid.nycnet:636')
    conn.start_tls_s()
    # Gives server down

# .ENV VARS
# LDAP_PROVIDER_URL = 'ldaps://ldaps-dev.nycid.nycnet:636/'
# LDAP_LOGIN_VIEW = 'login'
# LDAP_LOGIN_TEMPLATE = 'login.html'


def set_env(key, default=None):
    ''' Used to set environment variables '''
    if key in environ:
        app.config[key] = environ[key]
    elif key in app.config:
        pass
    elif default:
        app.config[key] = default


# UPDATES TO THESE DEFAULTS SHOULD OCCUR IN YOUR .env FILE.
set_env(key='TIMEZONE', default=pytz.timezone(str(get_localzone())))

# Set rest of the variables that don't have defaults:
envvars = [
    # Application Settings
    'AGENCY_NAME', # City Government Name
    'LIAISONS_URL', # Path to Records Liaison file
    'STAFF_URL', # Path to Records Staff file
    'LIST_OF_ADMINS', # List of System Administrators
    'DEFAULT_MAIL_SENDER', # Default from address
    'DEFAULT_OWNER_EMAIL', # Default email for Portal Administrator
    'DEFAULT_OWNER_REASON', # Default Title for Portal Administrator
    'DAYS_AFTER_EXTENSION', # Default number of days for an extension
    'DAYS_TO_FULFILL', # Default number of days to fulfill a request
    'DAYS_UNTIL_OVERDUE', # Default number of days until

    # Flask Settings
    'APPLICATION_URL', # Application URL
    'ENVIRONMENT', # Local Environemnt (LOCAL, STAGING, TESTING, PRODUCTION)
    'SECRET_KEY', # Secret key for cookie signing (sessions)
    'DATABASE_URL', # URL to access Postgres database

    # Flask Mail Settings
    'MAIL_USERNAME', # Username for mail server
    'MAIL_PASSWORD', # Password for mail server
    'MAIL_SERVER', # Mail Server URL
    'MAIL_USE_TLS', # TLS Setting for Mail Server
    'MAIL_PORT', # Port for SMTP
    'DEV_EMAIL', # Enable email sending on Local environment

    # Upload Settings
    'UPLOAD_DOCS', # Enable uploads of documents on Local environment
    'UPLOAD_FOLDER', # Path for uploaded documents
    'HOST_URL', # URL for uploaded documents folder

    # ReCaptcha
    'RECAPTCHA_SECRET_KEY', # Secret key for Google ReCaptcha
    'RECAPTCHA_SITE_KEY', # Site key for Google ReCaptcha

]

for envvar in envvars:
    set_env(key=envvar)

# Database gets set slightly differently, to support difference between Flask and Heroku naming:
app.config['SQLALCHEMY_DATABASE_URI'] = environ['DATABASE_URL']

# Initialize database
db = SQLAlchemy(app)

# Initialiaze ReCapthca
recaptcha = ReCaptcha(app)
