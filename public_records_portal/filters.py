from datetime import datetime, timedelta
from public_records_portal import app
from prr import *
import os

# Filters

app.jinja_env.filters['get_requester'] = get_requester
app.jinja_env.filters['is_request_open'] = is_request_open
app.jinja_env.filters['get_scribd_download_url'] = get_scribd_download_url
app.jinja_env.filters['last_note'] = last_note


@app.template_filter('due_date')
def due_date(obj):
	if not obj:
		return None
	if type(obj) is not datetime:
		obj = datetime.strptime(obj, "%Y-%m-%dT%H:%M:%S.%f")
	due_date = obj + timedelta(days = 10)
	return format_date(due_date.date())

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
	if oid:
		owner = get_resource("owner", oid)
		if owner and owner['user_id']:
			return user_name(owner['user_id'])
	return "City staff"

@app.template_filter('owner_uid')
def owner_uid(oid):
	if oid:
		owner = get_resource("owner", oid)
		if owner and owner['user_id']:
			return owner['user_id']
	return None

@app.template_filter('subscriber_name')
def subscriber_name(sid):
	if sid:
		subscriber = get_resource("subscriber", sid)
		if subscriber and subscriber['user_id']:
			return user_alias(subscriber['user_id'])
	return "Requester"

@app.template_filter('subscriber_phone')
def subscriber_phone(sid):
	if sid:
		subscriber = get_resource("subscriber", sid)
		if subscriber and subscriber['user_id']:
			return user_phone(subscriber['user_id'])
	return None

@app.template_filter('user_phone')
def user_phone(uid):
	if uid:
		user = User.query.get(uid)
		if user.phone:
			return user.phone
	return "Not given"

@app.template_filter('user_name')
def user_name(uid):
	if uid:
		user = User.query.get(uid)
		if user:
			if user.alias:
				return user.alias
			else:
				return user.email

	return "Requester"

@app.template_filter('user_email')
def user_email(uid):
	if uid:
		user = User.query.get(uid)
		if user:
			return user.email
	return None

def user_alias(uid):
	if uid:
		user = User.query.get(uid)
		if user.alias:
			return user.alias
	return "Not given"

@app.template_filter('explain_action')
def explain_action(action, explanation_type = None):
	# Get filepath for actions.json
	actions_filepath = os.path.join(app.root_path, 'actions.json')
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
		return explanation_str


@app.template_filter('directory')
def directory(uid, info_type = None):
	email =  user_email(uid)
	if email:
		if info_type == "email":
			return email
		dir_json = open(os.path.join(app.root_path, 'static/directory.json'))
		json_data = json.load(dir_json)
		for line in json_data:
			if line['EMAIL_ADDRESS'].lower() == email.lower():
				if info_type == 'name':
					last, first = line['FULL_NAME'].split(",")
					return "%s %s" % (first, last)
				if info_type == 'dept':
					return line['DEPARTMENT']
		if info_type == 'name':
			local,domain = email.split('@')
			name = "%s. %s" %(local[0].upper(), local[1:].title())
			return name
	return None

