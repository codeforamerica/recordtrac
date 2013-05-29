""" Things one can do relating to a public records request. """

from public_records_portal import app, models, website_copy
from models import *
import os
import tempfile
import scribd # Used for uploading documents, could use another service
import time
import requests as seaturtle # HTTP requests library, renaming because it's confusing otherwise
import json
from flask import Flask, render_template, request, flash, redirect, url_for
from flask.ext.sqlalchemy import SQLAlchemy, sqlalchemy
from sqlalchemy.exc import IntegrityError, InvalidRequestError
from werkzeug import secure_filename
import sendgrid

mail = sendgrid.Sendgrid(app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'], secure = True)
if app.config['ENVIRONMENT'] == "STAGING":
	app_url = app.config['APPLICATION_URL']
elif app.config['ENVIRONMENT'] == 'PRODUCTION':
	app_url = None
else:
	app_url = "http://127.0.0.1:8000/"

# Define the local temporary folder where uploads will go
if app.config['ENVIRONMENT'] == "PRODUCTION":
	UPLOAD_FOLDER = None # To do
elif app.config['ENVIRONMENT'] == "STAGING":
	UPLOAD_FOLDER = "/app" 
else:
	UPLOAD_FOLDER = "%s/uploads" % os.getcwd()
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'doc', 'ps', 'rtf', 'epub', 'key', 'odt', 'odp', 'ods', 'odg', 'odf', 'sxw', 'sxc', 'sxi', 'sxd', 'ppt', 'pps', 'xls', 'zip', 'docx', 'pptx', 'ppsx', 'xlsx', 'tif', 'tiff'])

def get_resource(resource, resource_id, url = None):
	url = app_url
	headers = {'Content-Type': 'application/json'}
	r = seaturtle.get("%s/api/%s/%s" %(url, resource, resource_id), headers=headers)
	if r:
		return r.json()
	return None

def get_resource_filter(resource, filters, url = None):
	url = app_url
	headers = {'Content-Type': 'application/json'}
	params = dict(q=json.dumps(dict(filters=filters)))
	r = seaturtle.get("%s/api/%s" %(url, resource), params=params, headers = headers)
	if r:
		return r.json()
	return None

def get_resources(resource, url = None):
	url = app_url
	headers = {'content-type': 'application/json; charset=utf-8'}
	r = seaturtle.get("%s/api/%s" %(url, resource), headers=headers)
	if r:
		return r.json()
	return None

def add_resource(resource, request_body, current_user_id = None):
	fields = request_body.form
	if "note" in resource:
		add_note(fields['request_id'], fields['note_text'], current_user_id)
	elif "record" in resource:
		upload_record(fields['request_id'], request.files['record'], fields['record_description'])
	elif "link" in resource:
		add_link(fields['request_id'], fields['link_url'], fields['link_description'])
	elif "qa" in resource:
		ask_a_question(fields['request_id'], fields['user_id'], fields['question_text'])
	else:
		return False
	return True

def create_resource(resource, payload, url = None):
	url = app_url
	r = seaturtle.post("%s/api/%s" %(url, resource), data=json.dumps(payload))
	if r:
		return r.json()
	return None

def delete_resource(resource, resource_id, url = None):
	url = app_url
	r = seaturtle.delete("%s/api/%s/%s" %(url, resource, resource_id))
	if r.status_code == '204':
		return True
	return False

def put_resource(resource, payload, resource_id, url = None):
	url = app_url
	r = seaturtle.put("%s/api/%s/%s" %(url, resource, resource_id), data=json.dumps(payload))
	if r.status_code == '201':
		return True
	return False

def update_resource(resource, request_body):
	fields = request_body.form
	if "qa" in resource:
		answer_a_question(fields['qa_id'], fields['answer_text'], fields['user_id'])
		return True
	else:
		return False

def add_note(request_id, text, user_id):
	note = Note(request_id = request_id, text = text, user_id = user_id)
	db.session.add(note)
	db.session.commit()
	change_request_status(request_id, "A response has been added.")
	send_prr_email(request_id = request_id, notification_type = "Response added", requester_id = get_requester(request_id))

def upload_record(request_id, file, description):
	doc_id, filename = upload_file(file)
	req = get_resource("request", request_id)
	if str(doc_id).isdigit():
		record = Record(doc_id = doc_id, request_id = request_id, owner_id = req['current_owner'], description = description)
		db.session.add(record)
		db.session.commit()
		record.filename = filename
		record.url = app.config['HOST_URL'] + doc_id
		db.session.commit()
		change_request_status(request_id, "A response has been added.")
		send_prr_email(request_id = request_id, notification_type = "Response added", requester_id = get_requester(request_id))
	else:
		return "Not an allowed doc type"

def add_link(request_id, url, description):
	req = get_resource("request", request_id)
	record = Record(url = url, request_id = request_id, owner_id = req['current_owner'], description = description)
	db.session.add(record)
	db.session.commit()
	change_request_status(request_id, "A response has been added.")
	send_prr_email(request_id = request_id, notification_type = "Response added", requester_id = get_requester(request_id))
			
def make_request(text, email = None, assigned_to_name = None, assigned_to_email = None, assigned_to_reason = None, user_id = None):
	""" Make the request. At minimum you need to communicate which record(s) you want, probably with some text."""
	resource = get_resource_filter("request", [dict(name='text', op='eq', val=text)])
	if not resource or not resource['objects']:
		payload = dict(text=text)
		if user_id:
			payload = dict(text=text, creator_id = user_id)
		req = create_resource("request", payload)
		past_owner_id, owner_id = assign_owner(request_id = req['id'], reason = assigned_to_reason, email = assigned_to_email, alias = assigned_to_name)
		if email: # If the user provided an e-mail address, add them as a subscriber to the request.
			user = create_or_return_user(email = email)
			subscriber = Subscriber(request_id = req['id'], user_id = user['id'])
			subscriber.creator = True
			db.session.add(subscriber)
			db.session.commit()
		open_request(req['id'])
		return req['id'], True
	return resource['objects'][0]['id'], False

def ask_a_question(request_id, user_id, question):
	""" City staff can ask a question about a request they are confused about."""
	qa = QA(request_id = request_id, question = question)
	qa.owner_id = user_id
	db.session.add(qa)
	db.session.commit()
	change_request_status(request_id, "Pending")
	send_prr_email(request_id = qa.request_id, notification_type = "Question asked", requester_id = get_requester(request_id))
	return qa.id

def answer_a_question(qa_id, answer, subscriber_id = None):
	""" A requester can answer a question city staff asked them about their request."""
	qa = get_resource("qa", qa_id)
	put_resource("qa", dict(subscriber_id = subscriber_id, answer = answer),int(qa_id))
	change_request_status(qa['request_id'], "Pending")
	# change_request_status(request_id, "%s needs to take action." %) # Pass the buck to the current owner
	req = get_resource("request", qa['request_id'])
	send_prr_email(request_id = qa['request_id'], notification_type = "Question answered", owner_id = req['current_owner'])

def create_or_return_user(email, alias = None):
	resource = get_resource_filter("user", [dict(name='email', op='eq', val=email)])
	if not resource['objects']:
		user = create_resource("user", dict(email = email, alias = alias))
		return user
	return resource['objects'][0]

def open_request(request_id):
	change_request_status(request_id, "Open")

def close_request(request_id, reason = ""):
	change_request_status(request_id, "Closed. %s" %reason)
	send_prr_email(request_id = request_id, notification_type = "Request closed", requester_id = get_requester(request_id))

def get_subscribers(request_id):
	req = get_resource("request", request_id)
	return req['subscribers']

def get_requester(request_id):
	subscribers = get_subscribers(request_id)
	for subscriber in subscribers:
		return subscriber['id'] # Return first one for now
		# if 'creator' in subscriber:
		# 	if subscriber['creator'] == True:
		# 		return subscriber.id

def assign_owner(request_id, reason, email = None, alias = None): 
	""" Called any time a new owner is assigned. This will overwrite the current owner."""
	user = create_or_return_user(email = email, alias = alias)
	req = get_resource("request", request_id)
	current_owner_id = None
	if not req['current_owner']:
		current_owner_id = req['current_owner']
	owner = None
	owner_resource = get_resource_filter("owner", [dict(name='request_id', op='eq', val=int(request_id)), dict(name='user_id', op='eq', val=int(user['id']))])
	if owner_resource['objects']:
		owner = owner_resource['objects']['0']
	if current_owner_id and owner:
		if current_owner_id == owner['id']:
			return None, None
	new_owner = create_resource("owner", dict(request_id = request_id, user_id = user['id'], reason = reason))
	if current_owner_id:
		past_owner_id = current_owner_id
	else:
		past_owner_id = None
	put_resource("request", dict(current_owner = new_owner['id']) ,int(request_id))
	change_request_status(request_id, "Pending")
	send_prr_email(request_id = request_id, notification_type = "Request assigned", owner_id = new_owner['id'])
	return past_owner_id, new_owner['id']

def change_request_status(request_id, status):
	return put_resource("request", dict(status = status, status_updated = datetime.now().isoformat()),int(request_id))

def progress(bytes_sent, bytes_total):
    print("%s of %s (%s%%)" % (bytes_sent, bytes_total, bytes_sent*100/bytes_total))

def upload(filepath, API_KEY, API_SECRET):
    # Configure the Scribd API.
    print "This is the filepath passed to upload %s" %(filepath)
    scribd.config(API_KEY, API_SECRET)
    doc_id = None
    try:
        # Upload the document from a file.
        doc = scribd.api_user.upload(
            open(filepath,'rb'),
            progress_callback=progress,
            req_buffer = tempfile.TemporaryFile()
            )
        # Poll API until conversion is complete.
        while doc.get_conversion_status() != 'DONE':
            # Sleep to prevent a runaway loop that will block the script.
            time.sleep(2)        
        doc_id = doc.id
        return doc_id
    except scribd.ResponseError, err:
        print 'Scribd failed: code=%d, error=%s' % (err.errno, err.strerror)
        return err.strerror

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
	return '.' in filename and \
		filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

def email_validation(email):
	name, domain = email.split("@")
	if domain == "oakland.net" or domain == "oaklandnet.com" or domain == "codeforamerica.org":
		return True
	return False

def upload_file(file): 
# Uploads file to scribd.com and returns doc ID. File can be accessed at scribd.com/doc/id
	if file and allowed_file(file.filename):
		filename = secure_filename(file.filename)
		filepath = os.path.join(UPLOAD_FOLDER, filename)
		print "This is the filepath: %s" % (filepath)
		file.save(filepath)
		doc_id = upload(filepath, app.config['SCRIBD_API_KEY'], app.config['SCRIBD_API_SECRET'])
		return doc_id, filename
	return None, None

def send_prr_email(request_id, notification_type, requester_id = None, owner_id = None):
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
	if app.config['ENVIRONMENT'] == "PRODUCTION":
		print "%s to %s with subject %s" % (render_template("generic_email.html", page = page), email_address, email_subject)
	else:
		send_email(render_template("generic_email.html", page = page), email_address, email_subject)

def get_user_email(uid):
	user = get_resource("user", uid)
	return user['email']

def send_email(body, recipient, subject):
	sender = app.config['DEFAULT_MAIL_SENDER']
	plaintext = ""
	html = body
	message = sendgrid.Message(sender, subject, plaintext, html)
	message.add_to(recipient)
	message.add_bcc(sender)
	mail.web.send(message)



