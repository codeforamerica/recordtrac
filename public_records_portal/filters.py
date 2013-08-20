from datetime import datetime, timedelta
from public_records_portal import app
from prr import *
import os
from jinja2 import Markup
from gravatar import get_gravatar_url

# Filters

app.jinja_env.filters['get_requester'] = get_requester
app.jinja_env.filters['is_request_open'] = is_request_open
app.jinja_env.filters['get_scribd_download_url'] = get_scribd_download_url
app.jinja_env.filters['last_note'] = last_note
app.jinja_env.filters['due_date'] = due_date
app.jinja_env.filters['get_staff_info'] = get_staff_info
app.jinja_env.filters['get_staff'] = get_staff
app.jinja_env.filters['date_granular'] = date_granular
app.jinja_env.filters['user_email'] = user_email
app.jinja_env.filters['get_responses_chronologically'] = get_responses_chronologically
app.jinja_env.filters['get_request_data_chronologically'] = get_request_data_chronologically
app.jinja_env.filters['owner_name'] = owner_name
app.jinja_env.filters['owner_uid'] = owner_uid
app.jinja_env.filters['subscriber_name'] = subscriber_name
app.jinja_env.filters['subscriber_phone'] = subscriber_phone
app.jinja_env.filters['subscriber_email'] = subscriber_email
app.jinja_env.filters['user_phone'] = user_phone
app.jinja_env.filters['user_name'] = user_name
app.jinja_env.filters['user_alias'] = user_alias
app.jinja_env.filters['get_gravatar_url'] = get_gravatar_url


@app.template_filter('new_lines')
def new_lines(value): 
	new_value = value.replace('\n','<br>\n')
	if value != new_value:
		return Markup(new_value)
	return value

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


@app.template_filter('explain_action')
def explain_action(action, explanation_type = None):
	# Get filepath for actions.json
	actions_filepath = os.path.join(app.root_path, 'static/json/actions.json')
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


@app.template_filter('tutorial')
def tutorial(section):
	# Get filepath for actions.json
	tutorial_filepath = os.path.join(app.root_path, 'static/json/tutorial.json')
	tutorial_json = open(tutorial_filepath)
	json_data = json.load(tutorial_json)
	explanation = json_data[section]
	return explanation

@app.template_filter('directory')
def directory(uid, info_type = None):
	email =  user_email(uid)
	if email:
		if info_type == "email":
			return email
		dir_json = open(os.path.join(app.root_path, 'static/json/directory.json'))
		json_data = json.load(dir_json)
		for line in json_data:
			if line['EMAIL_ADDRESS'].lower() == email.lower():
				if info_type == 'name':
					last, first = line['FULL_NAME'].split(",")
					return "%s %s" % (first, last)
				if info_type == 'dept':
					return line['DEPARTMENT']
		# if info_type == 'name':
		# 	local,domain = email.split('@')
		# 	name = "%s. %s" %(local[0].upper(), local[1:].title())
		# 	return name
	return None

