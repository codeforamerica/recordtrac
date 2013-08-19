""" 
.. module:: prr
	:synopsis: Things one can do relating to a public records request.
.. modlueauthor:: Richa Agarwal <richa@codeforamerica.org>
"""

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
from models import *
from timeout import timeout
import urllib
from ResponsePresenter import ResponsePresenter
from RequestPresenter import RequestPresenter
from flask.ext.sqlalchemy import SQLAlchemy, sqlalchemy
from sqlalchemy import func

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


def add_resource(resource, request_body, current_user_id = None):
	fields = request_body.form
	if "extension" in resource:
		req = Request.query.get(int(fields['request_id']))
		req.extended = True
		db.session.add(req)
		db.session.commit()
		extension_reasons = fields.getlist('note_text')
		text = "Request extended:"
		for reason in extension_reasons:
			text = text + reason + "</br>"
		return add_note(int(fields['request_id']), text, current_user_id)
	if "note" in resource:
		return add_note(int(fields['request_id']), fields['note_text'], current_user_id)
	elif "record" in resource:
		if fields['record_description'] == "":
			return "When uploading a record, please fill out the 'summary' field."
		if 'record_access' in fields and fields['record_access'] != "":
			return add_offline_record(int(fields['request_id']), fields['record_description'], fields['record_access'], current_user_id)
		elif 'link_url' in fields and fields['link_url'] != "":
			return add_link(int(fields['request_id']), fields['link_url'], fields['record_description'], current_user_id)
		else:
			return upload_record(int(fields['request_id']), request.files['record'], fields['record_description'], current_user_id)
	elif "qa" in resource:
		return ask_a_question(int(fields['request_id']), current_user_id, fields['question_text'])
	else:
		return False

def update_resource(resource, request_body):
	fields = request_body.form
	if "QA_delete" in resource:
		qa = QA.query.get(int(fields['qa_id']))
		db.session.delete(qa)
		db.session.commit()
	elif "qa" in resource:
		return answer_a_question(int(fields['qa_id']), fields['answer_text'])
	elif "owner" in resource:
		change_request_status(int(fields['request_id']), "Rerouted")
		return assign_owner(int(fields['request_id']), fields['owner_reason'], fields['owner_email'])
	elif "reopen" in resource:
		change_request_status(int(fields['request_id']), "Reopened")
		return fields['request_id']
	elif "request_text" in resource:
		req = Request.query.get(int(fields['request_id']))
		req.text = fields['request_text']
		db.session.add(req)
		db.session.commit()
	elif "note_text" in resource:
		note = Note.query.get(int(fields['response_id'])) # Make sure response_id is being passed because this was request ID before
		note.text = fields['note_text']
		db.session.add(note)
		db.session.commit()
		# Need to store note text somewhere else (or just do delete here as well)
	elif "note_delete" in resource:
		# Need to store note somewhere else
		note = Note.query.get(int(fields['response_id']))
		db.session.delete(note)
		db.session.commit()
	elif "record_delete" in resource:
		req = Request.query.get(int(fields['request_id']))
		db.session.delete(req)
		db.session.commit()
		# Need to store record somewhere else and prompt them to delete from Scribd as well, if they'd like
	else:
		return False

def add_note(request_id, text, user_id):
	# Need to udpate this so if a requester is adding a note, the e-mail gets sent to city staff instead
	if not text or text == "":
		return False
	note = Note(request_id = request_id, text = text, user_id = user_id)
	db.session.add(note)
	db.session.commit()
	if note:
		change_request_status(request_id, "A response has been added.")
		if user_id:
			send_prr_email(request_id = request_id, notification_type = "Response added", requester_id = get_requester(request_id))
		else:
			req = Request.query.get(request_id)
			send_prr_email(request_id = request_id, notification_type = "Public note added", owner_id = req.current_owner)
		return note.id
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
			record = Record(doc_id = doc_id, request_id = request_id, user_id = user_id, description = description, filename = filename, url = app.config['HOST_URL'] + doc_id)
			db.session.add(record)
			db.session.commit()
			change_request_status(request_id, "A response has been added.")
			send_prr_email(request_id = request_id, notification_type = "Response added", requester_id = get_requester(request_id))
			return record.id
	return "There was an issue with your upload."

def add_offline_record(request_id, description, access, user_id):
	# record = create_resource("record", dict(request_id = request_id, user_id = user_id, access = access, description = description))
	record = Record(request_id = request_id, user_id = user_id, access = access, description = description)
	db.session.add(record)
	db.session.commit()
	if record:
		change_request_status(request_id, "A response has been added.")
		send_prr_email(request_id = request_id, notification_type = "Response added", requester_id = get_requester(request_id))
		return record.id
	return False

def add_link(request_id, url, description, user_id):
	# record = create_resource("record", dict(url = url, request_id = request_id, user_id = user_id, description = description))
	record = Record(url = url, request_id = request_id, user_id = user_id, description = description)
	db.session.add(record)
	db.session.commit()
	if record:
		change_request_status(request_id, "A response has been added.")
		send_prr_email(request_id = request_id, notification_type = "Response added", requester_id = get_requester(request_id))
		return record.id
	return False
			
def make_request(text, email = None, assigned_to_name = None, assigned_to_email = None, assigned_to_reason = None, user_id = None, phone = None, alias = None):
	""" Make the request. At minimum you need to communicate which record(s) you want, probably with some text."""
	req = Request.query.filter_by(text = text).first()
	if not req:
		req = Request(text = text, creator_id = user_id)
		db.session.add(req)
		db.session.commit()
		new_owner_id = assign_owner(request_id = req.id, reason = assigned_to_reason, email = assigned_to_email, alias = assigned_to_name)
		if email: # If the user provided an e-mail address, add them as a subscriber to the request.
			user = create_or_return_user(email = email, alias = alias, phone = phone)
			subscriber = Subscriber(request_id = req.id, user_id = user.id)
			db.session.add(subscriber)
			db.session.commit()
			send_prr_email(req.id, notification_type = "Request made", requester_id = subscriber.id)
		open_request(req.id)
		return req.id, True
	return req.id, False

def ask_a_question(request_id, owner_id, question):
	""" City staff can ask a question about a request they are confused about."""
	# qa = create_resource("qa", dict(request_id = request_id, question = question, owner_id = owner_id))
	qa = QA(request_id = request_id, question = question, owner_id = owner_id)
	db.session.add(qa)
	db.session.commit()
	if qa:
		change_request_status(request_id, "Pending")
		send_prr_email(request_id, notification_type = "Question asked", requester_id = get_requester(request_id))
		return qa.id
	return False

def answer_a_question(qa_id, answer, subscriber_id = None):
	""" A requester can answer a question city staff asked them about their request."""
	qa = QA.query.get(qa_id)
	qa.subscriber_id = subscriber_id
	qa.answer = answer
	db.session.add(qa)
	db.session.commit()
	change_request_status(qa.request_id, "Pending")
	req = Request.query.get(qa.request_id)
	send_prr_email(request_id = qa.request_id, notification_type = "Question answered", user_id = qa.owner_id)

def create_or_return_user(email, alias = None, phone = None, department = None):
	user = User.query.filter(func.lower(User.email) == func.lower(email)).first() 
	if not user:
		user = User(email = email, alias = alias, phone = phone, department = department, password = app.config['ADMIN_PASSWORD'])
	else:
		if alias:
			user.alias = alias
		if phone:
			user.phone = phone
		if department:
			user.department = department
	if not user.password:
		user.password = app.config['ADMIN_PASSWORD']
	db.session.add(user)
	db.session.commit()
	return user

def last_note(request_id):
	req = Request.query.get(request_id) 
	if req.notes:
		return req.notes[0]
	return None

def open_request(request_id):
	change_request_status(request_id, "Open")

def close_request(request_id, reason = "", current_user_id = None):
	req = Request.query.get(request_id)
	current_owner = Owner.query.get(req.current_owner)
	change_request_status(request_id, "Closed")
	# Create a note to capture closed information:
	note = Note(request_id = request_id, text = reason, user_id = current_user_id)
	db.session.add(note)
	db.session.commit()
	send_prr_email(request_id = request_id, notification_type = "Request closed", requester_id = get_requester(request_id))

def get_subscribers(request_id):
	req = Request.query.get(request_id)
	return req.subscribers

def get_requester(request_id):
	subscribers = get_subscribers(request_id)
	for subscriber in subscribers:
		return subscriber.id # Return first one for now

def assign_owner(request_id, reason, email = None, alias = None, phone = None, notify = True): 
	""" Called any time a new owner is assigned. This will overwrite the current owner."""
	user = create_or_return_user(email = email, alias = alias, phone = phone)
	req = Request.query.get(request_id)
	current_owner_id = None
	if not req.current_owner:
		current_owner_id = req.current_owner
	owner = Owner.query.filter_by(request_id = int(request_id), user_id = int(user.id)).first()
	if current_owner_id and owner:
		if current_owner_id == owner.id:
			return None, None
	new_owner = Owner(request_id = request_id, user_id = user.id, reason = reason)
	db.session.add(new_owner)
	db.session.commit()
	req.current_owner = new_owner.id
	db.session.add(req)
	db.session.commit()
	if notify:
		send_prr_email(request_id = request_id, notification_type = "Request assigned", owner_id = new_owner.id)
	return new_owner.id

def create_owner(request_id, reason, email):
	""" Adds a staff member to the request without assigning them as current owner. (i.e. "participant")
	Useful for multidepartmental requests."""
	user = create_or_return_user(email = email)
	participant = Owner(request_id = request_id, user_id = user.id, reason = reason)
	db.session.add(participant)
	db.session.commit()
	return participant.id

def change_request_status(request_id, status):
	req = Request.query.get(request_id)
	req.status = status
	req.status_updated = datetime.now().isoformat()
	db.session.add(req)
	db.session.commit()

def is_request_open(request_id):
	req = Request.query.get(request_id)
	if req.status and 'Closed' in req.status:
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
	record = Record.query.get(record_id)
	record.download_url = download_url
	db.session.add(record)
	db.session.commit()

def scribd_batch_download(): 
	req = Request.query.all()
	for record in req.records:
		if record.download_url:
			urllib.urlretrieve(record.downlaod_url, "saved_records/%s" %(record.filename))

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

def send_prr_email(request_id, notification_type, requester_id = None, owner_id = None, user_id = None):
	app_url = app.config['APPLICATION_URL']
	template = "generic_email.html"
	if notification_type == "Request made":
		template = "new_request_email.html"
	email_json = open(os.path.join(app.root_path, 'static/json/emails.json'))
	json_data = json.load(email_json)
	email_subject = "Public Records Request %s: %s" %(request_id, json_data[notification_type])
	page = None
	uid = None
	include_unsubscribe_link = True
	if owner_id or user_id:
		page = "%scity/request/%s" %(app_url,request_id)
		if user_id:
			uid = user_id
		else:
			owner = Owner.query.get(owner_id)
			uid = owner.user_id
		include_unsubscribe_link = False # Only gets excluded for city staff
	if requester_id:
		page = "%srequest/%s" %(app_url,request_id)
		requester = Subscriber.query.get(requester_id)
		uid = requester.user_id
	email_address = user_email(uid)
	if email_address:
		try:
			if send_emails:
				send_email(render_template(template, page = page), [email_address], email_subject, include_unsubscribe_link = include_unsubscribe_link)
			else:
				print "%s to %s with subject %s" % (render_template("generic_email.html", page = page), email_address, email_subject)
		except:
			print "E-mail was not sent."

def user_email(uid):
	if uid:
		user = User.query.get(uid)
		if user:
			return user.email
	return None

def send_email(body, recipients, subject, include_unsubscribe_link = True):
	mail = sendgrid.Sendgrid(app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'], secure = True)
	sender = app.config['DEFAULT_MAIL_SENDER']
	plaintext = ""
	html = body
	message = sendgrid.Message(sender, subject, plaintext, html)
	if not include_unsubscribe_link:
		message.add_filter_setting("subscriptiontrack", "enable", 0)
	for recipient in recipients:
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
	num_days = 2
	if (current_date + timedelta(days = num_days)) == due:
		return True, due
	return False, due

def is_overdue(date_obj, extended = None):
	current_date = datetime.now().date()
	due = due_date(date_obj = date_obj, extended = extended, format = False)
	if (current_date >= due):
		return True, due
	return False, due

def notify_due():
	requests = Request.query.all()
	email_json = open(os.path.join(app.root_path, 'static/json/emails.json'))
	json_data = json.load(email_json)
	for req in requests:
		if "Closed" not in req.status:
			# Check if it is due in 2 days
			due_soon, date_due = is_due_soon(req.date_created, req.extended) 
			if due_soon:
				change_request_status(req.id, "Due soon")
				email_subject = "%sPublic Records Request %s: %s" %(test, req.id, json_data["Request due"])
			else:
				# Otherwise, check if it is overdue
				is_overdue, date_due = is_overdue(req.date_created, req.extended)
				if is_overdue:
					change_request_status(req.id, "Overdue")
					email_subject = "%sPublic Records Request %s: %s" %(test, req.id, json_data["Request overdue"])
				else:
					continue
			owner_email = user_email(owner_uid(req.current_owner)) # Get the e-mail address of the owner
			recipients = [owner_email]
			backup_email = get_dept_backup(owner_email)
			if backup_email:
				recipients.append(backup_email)
			app_url = app.config['APPLICATION_URL']
			page = "%scity/request/%s" %(app_url,req.id)
			body = "You can view the request and take any necessary action at the following webpage: <a href='%s'>%s</a>.</br></br> This is an automated message. You are receiving it because you are listed as the Public Records Request Liaison, Backup or Supervisor for your department." %(page, page)
				# Need to figure out a way to pass in generic email template outside application context. For now, hardcoding the body.
			send_email(body = body, recipients = recipients, subject = email_subject, include_unsubscribe_link = False)
def get_request_data_chronologically(req):
	public = False
	if current_user.is_anonymous():
		public = True
	responses = []
	if not req:
		return responses
	for i, note in enumerate(req.notes):
		if not note.user_id:
			responses.append(RequestPresenter(note = note, index = i, public = public, request = req))
	for i, qa in enumerate(req.qas):
		responses.append(RequestPresenter(qa = qa, index = i, public = public, request = req))
	if not responses:
		return responses
	responses.sort(key = lambda x:x.date(), reverse = True)
	return responses

def get_responses_chronologically(req):
	responses = []
	if not req:
		return responses
	for note in req.notes:
		if note.user_id:
			responses.append(ResponsePresenter(note = note))
	for record in req.records:
		responses.append(ResponsePresenter(record = record))
	if not responses:
		return responses
	responses.sort(key = lambda x:x.date(), reverse = True)
	if "Closed" in req.status:
		responses[0].set_icon("icon-lock icon-2x") # Set most recent note (closed note)'s icon
	return responses

def format_date(obj):
	return obj.strftime('%b %d, %Y')

def get_staff(uid):
	if uid:
		staff = User.query.get(uid)
		return staff
	return None

def get_staff_info(uid, info_type):
	if uid:
		staff = User.query.get(uid)
		if info_type == "email" and staff.email:
			return staff.email
		elif info_type == "phone" and staff.phone:
			return staff.phone
		elif info_type == "dept":
			return staff.department
		elif info_type == "name":
			return staff.alias
	return None

def set_directory_fields():
	dir_json = open(os.path.join(app.root_path, 'static/directory.json'))
	json_data = json.load(dir_json)
	for line in json_data:
		if line['EMAIL_ADDRESS']:
			try:
				last, first = line['FULL_NAME'].split(",")
			except:
				last, junk, first = line['FULL_NAME'].split(",")
			email = line['EMAIL_ADDRESS'].lower()
			user = create_or_return_user(email = email, alias = "%s %s" % (first, last), phone = line['PHONE'], department = line['DEPARTMENT'])

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

def owner_name(oid):
	if oid:
		owner = Owner.query.get(oid)
		if owner and owner.user_id:
			return user_name(owner.user_id)
	return "City staff"



def owner_uid(oid):
	if oid:
		owner = Owner.query.get(oid)
		if owner and owner.user_id:
			return owner.user_id
	return None


def subscriber_name(sid):
	if sid:
		subscriber = Subscriber.query.get(sid)
		if subscriber and subscriber.user_id:
			return user_alias(subscriber.user_id)
	return "Requester"


def subscriber_phone(sid):
	if sid:
		subscriber = Subscriber.query.get(sid)
		if subscriber and subscriber.user_id:
			return user_phone(subscriber.user_id)
	return None

def subscriber_email(sid):
	if sid:
		subscriber = Subscriber.query.get(sid)
		if subscriber and subscriber.user_id:
			return user_email(subscriber.user_id)

def user_phone(uid):
	if uid:
		user = User.query.get(uid)
		if user.phone:
			return user.phone
	return "Not given"

def user_name(uid):
	if uid:
		user = User.query.get(uid)
		if user:
			if user.alias:
				return user.alias
			else:
				return user.email
	return "Requester"


def user_alias(uid):
	if uid:
		user = User.query.get(uid)
		if user.alias:
			return user.alias
	return "Not given"

# Creates a file called doctypes.json from departments.json that is used by typeahead to map document types to the department which can fulfill it
def create_doctypes():
	depts = []
	depts_json = open(os.path.join(app.root_path, 'static/departments.json'))
	json_data = json.load(depts_json)
	for department in json_data:
		if "Council" in department:
			document_types = ['Council records']
		else:
			document_types = json_data[department]["Document Types"]
		for document_type in document_types:
			line = {}
			line['DEPARTMENT'] = department
			line['DOC_TYPE'] = document_type
			depts.append(line)
	with open(os.path.join(app.root_path, 'static/json/doctypes.json'), 'w') as outfile:
  		json.dump(depts, outfile)

def create_list_depts():
	depts = []
	depts_json = open(os.path.join(app.root_path, 'static/departments.json'))
	json_data = json.load(depts_json)
	for department in json_data:
		depts.append(department)
  	with open(os.path.join(app.root_path, 'static/list_of_departments.json'), 'w') as outfile:
  		json.dump(depts, outfile)

def get_prr_liaison(dept):
	depts_json = open(os.path.join(app.root_path, 'static/departments.json'))
	json_data = json.load(depts_json)
	if dept in json_data:
		return json_data[dept]["Contact"]
	return None

def get_dept_backup(dept_contact):
	depts_json = open(os.path.join(app.root_path, 'static/departments.json'))
	json_data = json.load(depts_json)
	for line in json_data:
		if json_data[line]["Contact"].lower() == dept_contact.lower():
			return json_data[line]["Backup"]
	return None

def testerrs(string):
	return 'hi'
