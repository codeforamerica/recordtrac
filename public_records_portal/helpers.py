"""
    public_records_portal.helpers
    ~~~~~~~~~~~~~~~~

    Implements various helper functions for RecordTrac

"""

from datetime import datetime, timedelta
import os
from public_records_portal import app
import json
from jinja2 import Markup
from db_helpers import *
import notifications
import pytz
from flask.ext.babel import gettext as _

def localize(datetime_str):
	tz = pytz.timezone(app.config['TIMEZONE'])
	return datetime_str.replace(tzinfo=pytz.utc).astimezone(tz) # This appears to work in Heroku but not locally

def date_granular(timestamp):
	if not timestamp:
		return None
	if type(timestamp) is not datetime:
		timestamp = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S.%f")
	delta = datetime.now() - timestamp
	days, hours, minutes, seconds = delta.days, delta.seconds//3600, delta.seconds//60, delta.seconds
	if days < 1:
		if hours > 1:
			return "%s hours ago" % hours
		elif minutes > 1:
			return "%s minutes ago" % minutes
		elif seconds > 1:
			return "%s seconds ago" % seconds
		else:
			return "Just now."
	elif days == 1:
		return "A day ago"
	elif days > 1:
		weeks = days//7
		if weeks < 1:
			return "%s days ago" % days
		if weeks == 1:
			return "A week ago"
		elif weeks > 1:
			return "%s weeks ago" % weeks


def date(obj):
	""" Take a datetime or datetime-like object and return a formatted date. """
	if not obj:
		return None
	try:
		return notifications.format_date(obj)
	except: # Not a datetime object
 		return notifications.format_date(datetime.strptime(obj, "%Y-%m-%dT%H:%M:%S.%f"))

def format_datetime(obj, format):
	""" Take a datetime or datetime-like object and return a formatted datetime string. """
	if not obj:
		return None
	try:
		return localize(obj).strftime(format)
	except: # Not a datetime object
		date_obj = datetime.strptime(obj, "%Y-%m-%dT%H:%M:%S.%f")
		return localize(date_obj).strftime(format)

def timestamp(obj):
	return localize(obj).strftime('%H:%M:%S')


def tutorial(section):
	# Get filepath for actions.json
	tutorial_filepath = os.path.join(app.root_path, 'static/json/tutorial.json')
	tutorial_json = open(tutorial_filepath)
	json_data = json.load(tutorial_json)
	explanation = json_data[section]
	return explanation

def explain_action(action, explanation_type = None):
	# Get filepath for actions.json
	actions_filepath = os.path.join(app.root_path, 'static/json/actions_' + _('en') + '.json')
	action_json = open(actions_filepath)
	json_data = json.load(action_json)
	explanation = json_data[action]
	if explanation_type:
		return explanation[explanation_type]
	else:
		explanation_str = ""
		if 'What' in explanation:
			explanation_str = explanation_str + explanation['What']
		if 'Who' in explanation:
			explanation_str = explanation_str + " " + explanation['Who']
		if 'Action' in explanation:
			explanation_str = explanation_str + " " + explanation['Action']
		return explanation_str.replace('*agency*', app.config['AGENCY_NAME'])


def clean_text(value):
	return unicode(Markup(value).striptags())

def new_lines(value):
	value = value.replace('\n','this_is_a_new_line')
	value = clean_text(value)
	value = value.replace('this_is_a_new_line','<br>')
	return Markup(value)

def display_staff_participant(owner, request):
	point_of_contact = request.point_person()
	if point_of_contact:
		if owner.id == request.point_person().id:
			return None
	staff = get_obj("User",owner.user_id)
	if not staff:
		return None
	if staff.alias:
		return staff.alias
	else:
		return staff.email
