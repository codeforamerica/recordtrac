from datetime import datetime, timedelta
from public_records_portal import app
from prr import *
import os

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
def date_granular(timestamp):
	if not timestamp:
		return None
	if type(timestamp) is not datetime:
		timestamp = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S.%f")
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
	owner = get_resource("owner", oid)
	user = get_resource("user", owner['user_id'])
	if user['alias']:
		return user['alias']
	return user['email']

@app.template_filter('subscriber_name')
def subscriber_name(sid):
	subscriber = get_resource("subscriber", sid)
	return user_name(subscriber['user_id'])

@app.template_filter('user_name')
def user_name(uid):
	user = get_resource("user", uid)
	if user['alias']:
		return user['alias']
	return user['email']

@app.template_filter('explain_action')
def explain_action(action):
	# Get filepath for actions.json
	actions_filepath = os.path.join(app.root_path, 'actions.json')
	action_json = open(actions_filepath)
	json_data = json.load(action_json)
	return json_data[action]