"""
A flask app to handle public records requests and display responses.

Initializes application and all of its environment variables.

.. moduleauthor:: Richa Agarwal <richa@codeforamerica.org>

"""

from os import environ, pardir
from os.path import abspath, dirname, join

import pytz
from dotenv import load_dotenv
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask_recaptcha import ReCaptcha
from tzlocal import get_localzone
import logging
from logging.handlers import TimedRotatingFileHandler
import time

# Initialize Flask app
app = Flask(__name__)
app.debug = True
log_filename =  "openrecords_"+time.strftime("%Y%m%d")+".log"
handler = TimedRotatingFileHandler(log_filename, when='D', interval=60)
handler.setLevel(logging.WARNING)
app.logger.addHandler(handler)

load_dotenv(abspath(join(join(dirname(__file__), pardir), '.env')))


def set_env(key, default=None):
    """ Used to set environment variables """
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
    'AGENCY_NAME',  # City Government Name
    'LIAISONS_URL',  # Path to Records Liaison file
    'STAFF_URL',  # Path to Records Staff file
    'LIST_OF_ADMINS',  # List of System Administrators
    'DEFAULT_MAIL_SENDER',  # Default from address
    'DEFAULT_OWNER_EMAIL',  # Default email for Portal Administrator
    'DEFAULT_OWNER_REASON',  # Default Title for Portal Administrator
    'DAYS_AFTER_EXTENSION',  # Default number of days for an extension
    'DAYS_TO_FULFILL',  # Default number of days to fulfill a request
    'DAYS_UNTIL_OVERDUE',  # Default number of days until
    'NYC_GOV_BASE', # Base URL for NYC.gov links/assets

    # Flask Settings
    'PUBLIC_APPLICATION_URL',  # Application URL for Public Users
    'AGENCY_APPLICATION_URL',  # Application URL for Agency Users
    'ENVIRONMENT',  # Local Environemnt (LOCAL, STAGING, TESTING, PRODUCTION)
    'SECRET_KEY',  # Secret key for cookie signing (sessions)
    'DATABASE_URL',  # URL to access Postgres database

    # Flask Mail Settings
    'MAIL_USERNAME',  # Username for mail server
    'MAIL_PASSWORD',  # Password for mail server
    'MAIL_SERVER',  # Mail Server URL
    'MAIL_USE_TLS',  # TLS Setting for Mail Server
    'MAIL_PORT',  # Port for SMTP
    'SEND_EMAILS',  # Enable email sending on Local environment

    # Upload Settings
    'UPLOAD_DOCS',  # Enable uploads of documents on Local environment
    'UPLOAD_FOLDER',  # Path for uploaded documents
    'HOST_URL',  # URL for uploaded documents folder

    # ReCaptcha
    'RECAPTCHA_SECRET_KEY',  # Secret key for Google ReCaptcha
    'RECAPTCHA_SITE_KEY',  # Site key for Google ReCaptcha

    # ICAP Variables
    'HOST',
    'SERVICE',
    'PORT',
    'SHOULD_SCAN_FILES',

    # LDAP
    'USE_LDAP', # Determines if LDAP or Flask-Login is used
    'LDAP_SERVER',  # LDAP Server URL
    'LDAP_PORT',  # LDAP Connection Port
    'LDAP_USE_TLS',  # Using TLS to connect to server
    'LDAP_CERT_PATH',  # Path to certificate. Required if using TLS
    'LDAP_SA_BIND_DN',  # Bind DN for the LDAP Service Account
    'LDAP_SA_PASSWORD',  # Password for the LDAP Service Account
    'LDAP_BASE_DN',  # Base DN for searching for users

]

for envvar in envvars:
    set_env(key=envvar)

# Database gets set slightly differently, to support difference between Flask and Heroku naming:
app.config['SQLALCHEMY_DATABASE_URI'] = environ['DATABASE_URL']

# Initialize database
db = SQLAlchemy(app)

# Initialiaze ReCapthca
recaptcha = ReCaptcha(app)

# Secure Cookie
from werkzeug.datastructures import CallbackDict
from flask.sessions import SessionInterface, SessionMixin
from itsdangerous import URLSafeTimedSerializer, BadSignature


class ItsdangerousSession(CallbackDict, SessionMixin):

    def __init__(self, initial=None):
        def on_update(self):
            self.modified = True
        CallbackDict.__init__(self, initial, on_update)
        self.modified = False


class ItsdangerousSessionInterface(SessionInterface):
    salt = 'cookie-session'
    session_class = ItsdangerousSession

    def get_serializer(self, app):
        if not app.secret_key:
            return None
        return URLSafeTimedSerializer(app.secret_key,
                                      salt=self.salt)

    def open_session(self, app, request):
        s = self.get_serializer(app)
        if s is None:
            return None
        val = request.cookies.get(app.session_cookie_name)
        if not val:
            return self.session_class()
        max_age = app.permanent_session_lifetime.total_seconds()
        try:
            data = s.loads(val, max_age=max_age)
            return self.session_class(data)
        except BadSignature:
            return self.session_class()

    def save_session(self, app, session, response):
        domain = self.get_cookie_domain(app)
        if not session:
            if session.modified:
                response.delete_cookie(app.session_cookie_name,
                                   domain=domain)
            return
        expires = self.get_expiration_time(app, session)
        val = self.get_serializer(app).dumps(dict(session))
        response.set_cookie(app.session_cookie_name, val,
                            expires=expires, httponly=True,
                            domain=domain)

app.session_interface = ItsdangerousSessionInterface()
