from datetime import datetime, timedelta
from public_records_portal import app
from prr import *
import os

# Filters

app.jinja_env.filters['get_requester'] = get_requester

@app.template_filter('date')
def date(obj):
	if not obj:
		return None
	try:
		return format_date(obj.date())
	except: # Not a datetime object
		try:
			return format_date(datetime.strptime(obj, "%Y-%m-%dT%H:%M:%S.%f").date())
		except:
			return format_date(obj) # Just return the thing, maybe it's already a date

def format_date(obj):
	return obj.strftime('%b %d, %Y')

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
	if owner:
		return user_name(owner['user_id'])
	return None

@app.template_filter('subscriber_name')
def subscriber_name(sid):
	subscriber = get_resource("subscriber", sid)
	return user_name(subscriber['user_id'])

@app.template_filter('subscriber_phone')
def subscriber_phone(sid):
	subscriber = get_resource("subscriber", sid)
	return user_phone(subscriber['user_id'])

@app.template_filter('user_phone')
def user_phone(uid):
	user = User.query.get(uid)
	if user.phone:
		return user.phone
	return None

@app.template_filter('user_name')
def user_name(uid):
	user = User.query.get(uid)
	if user.alias:
		return user.alias
	return user.email


@app.template_filter('explain_action')
def explain_action(action):
	# Get filepath for actions.json
	actions_filepath = os.path.join(app.root_path, 'actions.json')
	action_json = open(actions_filepath)
	json_data = json.load(action_json)
	return json_data[action]['What']