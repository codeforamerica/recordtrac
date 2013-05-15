from datetime import datetime, timedelta
from public_records_portal import app
from prr import *
import os

# Get filepath for actions.json
actions_filepath = os.path.join(app.root_path, 'actions.json')

# Filters

@app.template_filter('date')
def date(obj):
	if not obj:
		return None
	try:
		return obj.date()
	except: # Not a datetime object
		try:
			return datetime.strptime(obj, "%Y-%m-%dT%H:%M:%S.%f").date()
		except:
			return obj # Just return the thing, maybe it's already a date

@app.template_filter('date_granular')
def date_granular(obj):
	if not obj:
		return None
	timestamp = datetime.strptime(obj, "%Y-%m-%dT%H:%M:%S.%f")
	delta = datetime.now() - timestamp
	days, hours, minutes, seconds = delta.days, delta.seconds//3600, delta.seconds//60, delta.seconds
	if days > 1:
		return "%s days ago" % days
	elif hours > 1:
		return "%s hours ago" % hours
	elif minutes > 1:
		return "%s minutes ago" % minutes
	elif seconds > 1:
		return "%s seconds ago" % seconds
	else:
		return "Just now."


@app.template_filter('owner_name')
def owner_name(oid):
	owner = get_resource("owner", app.config['APPLICATION_URL'], oid)
	user = get_resource("user", app.config['APPLICATION_URL'], owner['user_id'])
	if user['alias']:
		return user['alias']
	return user['email']

@app.template_filter('subscriber_name')
def subscriber_name(sid):
	subscriber = get_resource("subscriber", app.config['APPLICATION_URL'], sid)
	user = get_resource("user", app.config['APPLICATION_URL'], subscriber['user_id'])
	if user['alias']:
		return user['alias']
	return user['email']


@app.template_filter('explain_action')
def explain_action(action):
	action_json = open(actions_filepath)
	json_data = json.load(action_json)
	return json_data[action]