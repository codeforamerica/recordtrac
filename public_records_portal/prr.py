""" 
.. module:: prr
	:synopsis: Things one can do relating to a public records request.
.. modlueauthor:: Richa Agarwal <richa@codeforamerica.org>
"""

from public_records_portal import app, db_helpers
import os, time, json
from flask import Flask, request
from flask.ext.login import current_user
from datetime import datetime, timedelta
from models import *
from ResponsePresenter import ResponsePresenter
from RequestPresenter import RequestPresenter
from notifications import generate_prr_emails
import scribd_helpers
from db_helpers import *
from spam import is_spam
import logging

### @export "add_resource"
def add_resource(resource, request_body, current_user_id = None):
	fields = request_body.form
	if "extension" in resource:
		return request_extension(int(fields['request_id']), fields.getlist('extend_reason'), current_user_id)
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
	elif "owner" in resource:
		participant_id, new = add_staff_participant(request_id = fields['request_id'], email = fields['owner_email'], reason = fields['owner_reason'])
		if new:
			generate_prr_emails(request_id = fields['request_id'], notification_type = "Staff participant added", user_id = get_attribute("user_id", obj_id = participant_id, obj_type = "Owner"))
		return participant_id
	elif "subscriber" in resource:
		return add_subscriber(request_id=fields['request_id'], email = fields['follow_email'])
	else:
		return False

### @export "update_resource"
def update_resource(resource, request_body):
	fields = request_body.form
	if "QA_delete" in resource:
		remove_obj("QA", int(fields['qa_id']))
	elif "qa" in resource:
		return answer_a_question(int(fields['qa_id']), fields['answer_text'])
	elif "owner" in resource:
		if "reason_unassigned" in fields:
			return remove_staff_participant(owner_id = fields['owner_id'], reason = fields['reason_unassigned'])
		else:
			change_request_status(int(fields['request_id']), "Rerouted")
			return assign_owner(int(fields['request_id']), fields['owner_reason'], fields['owner_email'])
	elif "reopen" in resource:
		change_request_status(int(fields['request_id']), "Reopened")
		return fields['request_id']
	elif "request_text" in resource:
		update_obj(attribute = "text", val = fields['request_text'], obj_type = "Request", obj_id = fields['request_id'])
	elif "note_text" in resource:
		update_obj(attribute = "text", val = fields['note_text'], obj_type = "Note", obj_id = fields['response_id'])
		# Need to store note text somewhere else (or just do delete here as well)
	elif "note_delete" in resource:
		# Need to store note somewhere else
		remove_obj("Note", int(fields['response_id']))
	elif "record_delete" in resource:
		remove_obj("Record", int(fields['record_id']))
		# Need to store record somewhere else and prompt them to delete from Scribd as well, if they'd like
	else:
		return False

### @export "request_extension"
def request_extension(request_id, extension_reasons, user_id):
	req = Request.query.get(request_id)
	req.extension()
	text = "Request extended:"
	for reason in extension_reasons:
		text = text + reason + "</br>"
	add_staff_participant(request_id = request_id, user_id = user_id)
	return add_note(request_id = request_id, text = text, user_id = user_id)

### @export "add_note"
def add_note(request_id, text, user_id):
	if not text or text == "":
		return False
	note_id = create_note(request_id = request_id, text = text, user_id = user_id)
	if note_id:
		change_request_status(request_id, "A response has been added.")
		if user_id:
			add_staff_participant(request_id = request_id, user_id = user_id)
			generate_prr_emails(request_id = request_id, notification_type = "City response added")
		else:
			generate_prr_emails(request_id = request_id, notification_type = "Public note added")
		return note_id
	return False



### @export "upload_record"
def upload_record(request_id, file, description, user_id):
	""" Creates a record with upload/download attributes """
	try:
		doc_id, filename = scribd_helpers.upload_file(file = file, request_id = request_id)
	except:
		return "The upload timed out, please try again."
	if doc_id == False:
		return "Extension type '%s' is not allowed." % filename
	else:
		if str(doc_id).isdigit():
			record_id = create_record(doc_id = doc_id, request_id = request_id, user_id = user_id, description = description, filename = filename, url = app.config['HOST_URL'] + doc_id)
			change_request_status(request_id, "A response has been added.")
			generate_prr_emails(request_id = request_id, notification_type = "City response added")
			add_staff_participant(request_id = request_id, user_id = user_id)
			return record_id
	return "There was an issue with your upload."

### @export "add_offline_record"
def add_offline_record(request_id, description, access, user_id):
	""" Creates a record with offline attributes """
	record_id = create_record(request_id = request_id, user_id = user_id, access = access, description = description) # To create an offline record, we need to know the request ID to which it will be added, the user ID for the person adding the record, how it can be accessed, and a description/title of the record.
	if record_id:
		change_request_status(request_id, "A response has been added.")
		generate_prr_emails(request_id = request_id, notification_type = "City response added")
		add_staff_participant(request_id = request_id, user_id = user_id)
		return record_id
	return False

### @export "add_link"
def add_link(request_id, url, description, user_id):
	""" Creates a record with link attributes """
	record_id = create_record(url = url, request_id = request_id, user_id = user_id, description = description)
	if record_id:
		change_request_status(request_id, "A response has been added.")
		generate_prr_emails(request_id = request_id, notification_type = "City response added")
		add_staff_participant(request_id = request_id, user_id = user_id)
		return record_id
	return False

### @export "make_request"			
def make_request(text, email = None, user_id = None, phone = None, alias = None, department = None, passed_recaptcha = False):
	""" Make the request. At minimum you need to communicate which record(s) you want, probably with some text."""
	if (app.config['ENVIRONMENT'] == 'PRODUCTION') and (not passed_recaptcha) and is_spam(text): 
		return None, False
	request_id = find_request(text)
	if request_id: # Same request already exists
		return request_id, False
	assigned_to_email = app.config['DEFAULT_OWNER_EMAIL']
	assigned_to_reason = app.config['DEFAULT_OWNER_REASON']
	if department:
		app.logger.info("\n\nDepartment chosen: %s" %department)
		prr_email = db_helpers.get_contact_by_dept(department)
		if prr_email:
			assigned_to_email = prr_email
			assigned_to_reason = "PRR Liaison for %s" %(department)
		else:
			app.logger.info("%s is not a valid department" %(department))
			department = None
	request_id = create_request(text = text, user_id = user_id, department = department) # Actually create the Request object
	new_owner_id = assign_owner(request_id = request_id, reason = assigned_to_reason, email = assigned_to_email) # Assign someone to the request
	open_request(request_id) # Set the status of the incoming request to "Open"
	subscriber_user_id = create_or_return_user(email = email, alias = alias, phone = phone)
	subscriber_id, is_new_subscriber = create_subscriber(request_id = request_id, user_id = subscriber_user_id)
	if subscriber_id:
		generate_prr_emails(request_id, notification_type = "Request made", user_id = subscriber_user_id) # Send them an e-mail notification
	return request_id, True

### @export "add_subscriber"	
def add_subscriber(request_id, email):
	user_id = create_or_return_user(email = email)
	subscriber_id, is_new_subscriber = create_subscriber(request_id = request_id, user_id = user_id)
	if subscriber_id:
		generate_prr_emails(request_id, notification_type = "Request followed", user_id = user_id)
		return subscriber_id
	return False

### @export "ask_a_question"	
def ask_a_question(request_id, owner_id, question):
	""" City staff can ask a question about a request they are confused about."""
	req = get_obj("Request", request_id)
	qa_id = create_QA(request_id = request_id, question = question, owner_id = owner_id)
	if qa_id:
		change_request_status(request_id, "Pending")
		requester = req.requester()
		if requester:
			generate_prr_emails(request_id, notification_type = "Question asked", user_id = requester.user_id)
		add_staff_participant(request_id = request_id, user_id = get_attribute(attribute = "user_id", obj_id = owner_id, obj_type = "Owner"))
		return qa_id
	return False

### @export "answer_a_question"
def answer_a_question(qa_id, answer, subscriber_id = None):
	""" A requester can answer a question city staff asked them about their request."""
	request_id = create_answer(qa_id, subscriber_id, answer)
	# We aren't changing the request status if someone's answered a question anymore, but we could
	# change_request_status(request_id, "Pending")
	generate_prr_emails(request_id = request_id, notification_type = "Question answered")

### @export "open_request"	
def open_request(request_id):
	change_request_status(request_id, "Open")

### @export "assign_owner"	
def assign_owner(request_id, reason, email = None): 
	""" Called any time a new owner is assigned. This will overwrite the current owner."""
	req = get_obj("Request", request_id)
	past_owner_id = None
	# If there is already an owner, unassign them:
	if req.point_person():
		past_owner_id = req.point_person().id
		past_owner = get_obj("Owner", req.point_person().id)
		update_obj(attribute = "is_point_person", val = False, obj = past_owner)
	owner_id, is_new_owner = add_staff_participant(request_id = request_id, reason = reason, email = email, is_point_person = True)
	if (past_owner_id == owner_id): # Already the current owner, so don't send any e-mails
		return owner_id

	app.logger.info("\n\nA new owner has been assigned: Owner: %s" % owner_id)
	new_owner = get_obj("Owner", owner_id)	
	# Update the associated department on request
	update_obj(attribute = "department_id", val = new_owner.user.department, obj = req)
	user_id = get_attribute(attribute = "user_id", obj_id = owner_id, obj_type = "Owner")
	# Send notifications
	if is_new_owner:
		generate_prr_emails(request_id = request_id, notification_type = "Request assigned", user_id = user_id)
	return owner_id

### @export "get_request_data_chronologically"
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

### @export "get_responses_chronologically"
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
		responses[0].set_icon("icon-archive") # Set most recent note (closed note)'s icon
	return responses

### @export "set_directory_fields"
def set_directory_fields():
	dir_json = open(os.path.join(app.root_path, 'static/json/directory.json'))
	json_data = json.load(dir_json)
	staff_emails = []
	for line in json_data:
		if line['EMAIL_ADDRESS']:
			try:
				last, first = line['FULL_NAME'].split(",")
			except:
				last, junk, first = line['FULL_NAME'].split(",")
			email = line['EMAIL_ADDRESS'].lower()
			user = create_or_return_user(email = email, alias = "%s %s" % (first, last), phone = line['PHONE'], department = line['DEPARTMENT'])
			# Generate an updated json file that stores staff e-mails
			staff_emails.append(email)
	with open(os.path.join(app.root_path, 'static/json/staff_emails.json'), 'w') as outfile:
		json.dump(staff_emails, outfile)

### @export "last_note"
def last_note(request_id):
	notes = get_attribute(attribute = "notes", obj_id = request_id, obj_type = "Request")
	if notes:
		return notes[0]
	return None

### @export "close_request"
def close_request(request_id, reason = "", user_id = None):
	req = get_obj("Request", request_id)
	change_request_status(request_id, "Closed")
	# Create a note to capture closed information:
	create_note(request_id, reason, user_id)
	generate_prr_emails(request_id = request_id, notification_type = "Request closed")
	add_staff_participant(request_id = request_id, user_id = user_id)
