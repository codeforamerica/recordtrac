""" Things one can do relating to a public records request. """

from public_records_portal import app, website_copy, db
import os
import tempfile
import scribd # Used for uploading documents, could use another service
import time
import requests as seaturtle # HTTP requests library, renaming because it's confusing otherwise
import json
from flask import Flask, render_template, request
from flask.ext.login import current_user
from werkzeug import secure_filename
import sendgrid
from datetime import datetime, timedelta
from models import User
from timeout import timeout
import urllib

ALLOWED_EXTENSIONS = ['txt', 'pdf', 'doc', 'ps', 'rtf', 'epub', 'key', 'odt', 'odp', 'ods', 'odg', 'odf', 'sxw', 'sxc', 'sxi', 'sxd', 'ppt', 'pps', 'xls', 'zip', 'docx', 'pptx', 'ppsx', 'xlsx', 'tif', 'tiff']

# Set flags:
upload_to_scribd = False
send_emails = False
test = "[TEST] "
if app.config['ENVIRONMENT'] != 'LOCAL':
	upload_to_scribd = True
if app.config['ENVIRONMENT'] == 'PRODUCTION':
	send_emails = True
	test = ""

def get_resource(resource, resource_id, app_url = None):
	if not app_url:
		app_url = app.config['APPLICATION_URL']
	headers = {'Content-Type': 'application/json'}
	r = seaturtle.get("%s/api/%s/%s" %(app_url, resource, resource_id), headers=headers)
	if r:
		return r.json()
	return None

def get_resource_filter(resource, filters, app_url = None, order_by = None):
	if not app_url:
		app_url = app.config['APPLICATION_URL']
	headers = {'Content-Type': 'application/json'}
	if order_by:
		params = dict(q=json.dumps(dict(filters=filters, order_by = order_by)))
	else:
		params = dict(q=json.dumps(dict(filters=filters)))
	r = seaturtle.get("%s/api/%s" %(app_url, resource), params=params, headers = headers)
	if r:
		return r.json()
	return None

def get_resources(resource, app_url = None, order_by = None):
	if not app_url:
		app_url = app.config['APPLICATION_URL']
	headers = {'content-type': 'application/json; charset=utf-8'}
	params = None
	if order_by:
		params = dict(q=json.dumps(dict(order_by=order_by)))
	r = seaturtle.get("%s/api/%s" %(app_url, resource), params = params, headers=headers)
	if r:
		return r.json()
	return None

def add_resource(resource, request_body, current_user_id = None):
	fields = request_body.form
	if "note" in resource:
		return add_note(fields['request_id'], fields['note_text'], current_user_id)
	elif "record" in resource:
		if fields['record_description'] == "":
			return "When uploading a record, please fill out the 'summary' field."
		if 'record_access' in fields and fields['record_access'] != "":
			return add_offline_record(fields['request_id'], fields['record_description'], fields['record_access'], current_user_id)
		elif 'link_url' in fields and fields['link_url'] != "":
			return add_link(fields['request_id'], fields['link_url'], fields['record_description'], current_user_id)
		else:
			return upload_record(fields['request_id'], request.files['record'], fields['record_description'], current_user_id)
	elif "qa" in resource:
		return ask_a_question(fields['request_id'], current_user_id, fields['question_text'])
	else:
		return False

def create_resource(resource, payload, app_url = None):
	if not app_url:
		app_url = app.config['APPLICATION_URL']
	r = seaturtle.post("%s/api/%s" %(app_url, resource), data=json.dumps(payload))
	if r:
		return r.json()
	return None

def delete_resource(resource, resource_id, app_url = None):
	if not app_url:
		app_url = app.config['APPLICATION_URL']
	r = seaturtle.delete("%s/api/%s/%s" %(app_url, resource, resource_id))
	if r.status_code == '204':
		return True
	return False

def put_resource(resource, payload, resource_id, app_url = None):
	if not app_url:
		app_url = app.config['APPLICATION_URL']
	r = seaturtle.put("%s/api/%s/%s" %(app_url, resource, resource_id), data=json.dumps(payload))
	if r.status_code == '201':
		return True
	return False

def update_resource(resource, request_body):
	fields = request_body.form
	if "qa" in resource:
		return answer_a_question(fields['qa_id'], fields['answer_text'])
	elif "owner" in resource:
		change_request_status(fields['request_id'], "Rerouted")
		return assign_owner(fields['request_id'], fields['owner_reason'], fields['owner_email'])
	elif "reopen" in resource:
		change_request_status(fields['request_id'], "Reopened")
		return fields['request_id']
	elif "extend" in resource:
		extend_request(fields['request_id'])
		return fields['request_id']
	else:
		return False

def add_note(request_id, text, user_id):
	# Need to udpate this so if a requester is adding a note, the e-mail gets sent to city staff instead
	note = create_resource("note", dict(request_id = request_id, text = text, user_id = user_id))
	if note:
		change_request_status(request_id, "A response has been added.")
		send_prr_email(request_id = request_id, notification_type = "Response added", requester_id = get_requester(request_id))
		return note['id']
	return False

def upload_record(request_id, file, description, user_id):
	try:
		doc_id, filename = upload_file(file)
	except:
		return "The upload timed out, please try again."
	if doc_id == False:
		return "Extension type '%s' is not allowed." % filename
	else:
		if str(doc_id).isdigit():
			record = create_resource("record", dict(doc_id = doc_id, request_id = request_id, user_id = user_id, description = description, filename = filename, url = app.config['HOST_URL'] + doc_id))
			change_request_status(request_id, "A response has been added.")
			send_prr_email(request_id = request_id, notification_type = "Response added", requester_id = get_requester(request_id))
			return True
	return "There was an issue with your upload."

def add_offline_record(request_id, description, access, user_id):
	record = create_resource("record", dict(request_id = request_id, user_id = user_id, access = access, description = description))
	if record:
		change_request_status(request_id, "A response has been added.")
		send_prr_email(request_id = request_id, notification_type = "Response added", requester_id = get_requester(request_id))
		return record['id']
	return False

def extend_request(request_id):
	put_resource("request", dict(extended = True),int(request_id))
	# Create note etc

def add_link(request_id, url, description, user_id):
	record = create_resource("record", dict(url = url, request_id = request_id, user_id = user_id, description = description))
	if record:
		change_request_status(request_id, "A response has been added.")
		send_prr_email(request_id = request_id, notification_type = "Response added", requester_id = get_requester(request_id))
		return record['id']
	return False
			
def make_request(text, email = None, assigned_to_name = None, assigned_to_email = None, assigned_to_reason = None, user_id = None, phone = None, alias = None):
	""" Make the request. At minimum you need to communicate which record(s) you want, probably with some text."""
	resource = get_resource_filter("request", [dict(name='text', op='eq', val=text)])
	if not resource or not resource['objects']:
		payload = dict(text=text)
		if user_id:
			payload = dict(text=text, creator_id = user_id)
		req = create_resource("request", payload)
		new_owner_id = assign_owner(request_id = req['id'], reason = assigned_to_reason, email = assigned_to_email, alias = assigned_to_name)
		if email: # If the user provided an e-mail address, add them as a subscriber to the request.
			user = create_or_return_user(email = email, alias = alias, phone = phone)
			subscriber = create_resource("subscriber", dict(request_id = req['id'], user_id = user.id))
		open_request(req['id'])
		return req['id'], True
	return resource['objects'][0]['id'], False

def ask_a_question(request_id, owner_id, question):
	""" City staff can ask a question about a request they are confused about."""
	qa = create_resource("qa", dict(request_id = request_id, question = question, owner_id = owner_id))
	if qa:
		change_request_status(request_id, "Pending")
		send_prr_email(request_id, notification_type = "Question asked", requester_id = get_requester(request_id))
		return qa['id']
	return False

def answer_a_question(qa_id, answer, subscriber_id = None):
	""" A requester can answer a question city staff asked them about their request."""
	qa = get_resource("qa", qa_id)
	put_resource("qa", dict(subscriber_id = subscriber_id, answer = answer),int(qa_id))
	change_request_status(qa['request_id'], "Pending")
	req = get_resource("request", qa['request_id'])
	send_prr_email(request_id = qa['request_id'], notification_type = "Question answered", owner_id = qa['owner_id'])

def create_or_return_user(email, alias = None, phone = None):
	user = User.query.filter_by(email = email).first()
	if not user:
		user = User(email = email, alias = alias, phone = phone, password = app.config['ADMIN_PASSWORD'])
	else:
		if alias:
			user.alias = alias
		if phone:
			user.phone = phone
	if not user.password:
		user.password = app.config['ADMIN_PASSWORD']
	db.session.add(user)
	db.session.commit()
	return user

def last_note(request_id):
	notes = get_resource_filter(resource = "note", filters= [dict(name='request_id', op='eq', val=request_id)], order_by = [dict(field="date_created", direction="desc")])
	if notes['objects']:
		return notes['objects'][0]
	return None

def open_request(request_id):
	change_request_status(request_id, "Open")

def close_request(request_id, reason = "", current_user_id = None):
	req = get_resource("request", request_id)
	current_owner = get_resource("owner", req['current_owner'])
	change_request_status(request_id, "Closed")
	# Create a note to capture closed information:
	create_resource("note", dict(request_id = request_id, text = reason, user_id = current_user_id))
	send_prr_email(request_id = request_id, notification_type = "Request closed", requester_id = get_requester(request_id))

def get_subscribers(request_id):
	req = get_resource("request", request_id)
	return req['subscribers']

def get_requester(request_id):
	subscribers = get_subscribers(request_id)
	for subscriber in subscribers:
		return subscriber['id'] # Return first one for now

def assign_owner(request_id, reason, email = None, alias = None, phone = None, notify = True): 
	""" Called any time a new owner is assigned. This will overwrite the current owner."""
	user = create_or_return_user(email = email, alias = alias, phone = phone)
	req = get_resource("request", request_id)
	current_owner_id = None
	if not req['current_owner']:
		current_owner_id = req['current_owner']
	owner = None
	owner_resource = get_resource_filter("owner", [dict(name='request_id', op='eq', val=int(request_id)), dict(name='user_id', op='eq', val=int(user.id))])
	if owner_resource['objects']:
		owner = owner_resource['objects'][0]
	if current_owner_id and owner:
		if current_owner_id == owner['id']:
			return None, None
	new_owner = create_resource("owner", dict(request_id = request_id, user_id = user.id, reason = reason))
	put_resource("request", dict(current_owner = new_owner['id']) ,int(request_id))
	if notify:
		send_prr_email(request_id = request_id, notification_type = "Request assigned", owner_id = new_owner['id'])
	return new_owner['id']

def change_request_status(request_id, status):
	return put_resource("request", dict(status = status, status_updated = datetime.now().isoformat()),int(request_id))

def is_request_open(request_id):
	req = get_resource("request", request_id)
	if req['status'] and 'Closed' in req['status']:
		return False
	return True

def progress(bytes_sent, bytes_total):
    print("%s of %s (%s%%)" % (bytes_sent, bytes_total, bytes_sent*100/bytes_total))

def upload(file, filename, API_KEY, API_SECRET):
    # Configure the Scribd API.
    scribd.config(API_KEY, API_SECRET)
    doc_id = None
    try:
        # Upload the document from a file.
        doc = scribd.api_user.upload(
            targetfile = file,
            name = filename,
            progress_callback=progress,
            req_buffer = tempfile.TemporaryFile()
            )       
        doc_id = doc.id
        return doc_id
    except scribd.ResponseError, err:
        print 'Scribd failed: code=%d, error=%s' % (err.errno, err.strerror)
        return err.strerror

def get_scribd_download_url(doc_id, record_id = None, API_KEY = None, API_SECRET = None):
	if not API_KEY:
		API_KEY = app.config['SCRIBD_API_KEY']
	if not API_SECRET:
		API_SECRET = app.config['SCRIBD_API_SECRET']
	try:
		scribd.config(API_KEY, API_SECRET)
		doc = scribd.api_user.get(doc_id)
		doc_url = doc.get_download_url()
		if record_id:
			set_scribd_download_url(doc_url, record_id)
		return doc_url
	except:
		return None

def set_scribd_download_url(download_url, record_id):
	return put_resource("record", dict(download_url = download_url),int(record_id))

def scribd_batch_download(): 
	records = get_resources("record")
	for record in records['objects']:
		if record['download_url']:
			urllib.urlretrieve(record['download_url'], "saved_records/%s" %(record['filename']))

def make_public(doc_id, API_KEY, API_SECRET):
    scribd.config(API_KEY, API_SECRET)
    doc = scribd.api_user.get(doc_id)
    doc.access = 'public'
    doc.save()

def make_private(doc_id, API_KEY, API_SECRET):
    scribd.config(API_KEY, API_SECRET)
    doc = scribd.api_user.get(doc_id)
    doc.access = 'private'
    doc.save()

def allowed_file(filename):
	ext = filename.rsplit('.', 1)[1]
	return ext in ALLOWED_EXTENSIONS, ext

def email_validation(email):
	if email:
		name, domain = email.split("@")
		if domain in ['oakland.net', 'oaklandnet.com', 'codeforamerica.org', 'oaklandcityattorney.org']:
			return True
	return False

@timeout(seconds=20)
def upload_file(file): 
# Uploads file to scribd.com and returns doc ID. File can be accessed at scribd.com/doc/id
	if file:
		allowed = allowed_file(file.filename)
		if allowed[0]:
			filename = secure_filename(file.filename)
			if upload_to_scribd: # Check flag
				doc_id = upload(file, filename, app.config['SCRIBD_API_KEY'], app.config['SCRIBD_API_SECRET'])
				return doc_id, filename
			else:
				return '1', filename # Don't need to do real uploads locally
		else:
			return allowed # Returns false and extension
	return None, None

def send_prr_email(request_id, notification_type, requester_id = None, owner_id = None):
	app_url = app.config['APPLICATION_URL']
	email_json = open(os.path.join(app.root_path, 'emails.json'))
	json_data = json.load(email_json)
	email_subject = "Public Records Request %s: %s" %(request_id, json_data[notification_type])
	page = None
	uid = None
	if owner_id:
		page = "%scity/request/%s" %(app_url,request_id)
		owner = get_resource("owner", owner_id)
		uid = owner['user_id']
	if requester_id:
		page = "%srequest/%s" %(app_url,request_id)
		requester = get_resource("subscriber", requester_id)
		uid = requester['user_id']
	email_address = get_user_email(uid)
	if email_address:
		try:
			if send_emails:
				send_email(render_template("generic_email.html", page = page), email_address, email_subject)
			else:
				print "%s to %s with subject %s" % (render_template("generic_email.html", page = page), email_address, email_subject)
		except:
			print "E-mail was not sent."

def get_user_email(uid):
	if uid:
		user = User.query.get(uid)
		if user:
			return user.email
	else:
		return None

def send_email(body, recipient, subject):
	mail = sendgrid.Sendgrid(app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'], secure = True)
	sender = app.config['DEFAULT_MAIL_SENDER']
	plaintext = ""
	html = body
	message = sendgrid.Message(sender, subject, plaintext, html)
	message.add_to(recipient)
	message.add_bcc(sender)
	mail.web.send(message)

def due_date(date_obj, extended = None, format = True):
	days_to_fulfill = 10
	if extended == True:
		days_to_fulfill = days_to_fulfill + 14
	if not date_obj:
		return None
	if type(date_obj) is not datetime:
		date_obj = datetime.strptime(date_obj, "%Y-%m-%dT%H:%M:%S.%f")
	due_date = date_obj + timedelta(days = days_to_fulfill)
	if format:
		return format_date(due_date.date())
	return due_date.date()

def is_due_soon(date_obj, extended = None):
	current_date = datetime.now().date()
	due = due_date(date_obj = date_obj, extended = extended, format = False)
	num_days = 11
	if (current_date + timedelta(days = num_days)) == due:
		return True, due
	return False, due

def notify_due_soon():
	requests = get_resources("request")
	for req in requests['objects']:
		due_soon, date_due = is_due_soon(req['date_created'], req['extended'])
		if due_soon:
			owner = get_resource("owner", req['current_owner'])
			uid = owner['user_id']
			email_address = get_user_email(uid)
			email_json = open(os.path.join(app.root_path, 'emails.json'))
			json_data = json.load(email_json)
			email_subject = "%sPublic Records Request %s: %s" %(test, req['id'], json_data["Request due"])
			app_url = app.config['APPLICATION_URL']
			page = "%s/city/request/%s" %(app_url,req['id'])
			body = "You can view the request and take any necessary action at the following webpage: <a href='%s'>%s</a>" %(page, page)
			# Need to figure out a way to pass in generic email template outside application context. For now, hardcoding the body.
			send_email(body = body, recipient = email_address, subject = email_subject)
		else:
			print "You've got time. Due %s" %(date_due)

def format_date(obj):
	return obj.strftime('%b %d, %Y')
