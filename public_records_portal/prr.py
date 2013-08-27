""" 
.. module:: prr
	:synopsis: Things one can do relating to a public records request.
.. modlueauthor:: Richa Agarwal <richa@codeforamerica.org>
"""

from public_records_portal import app
import os
import time
import json
from flask import Flask, render_template, request
from flask.ext.login import current_user
from datetime import datetime, timedelta
from models import *
from ResponsePresenter import ResponsePresenter
from RequestPresenter import RequestPresenter
from notifications import generate_prr_emails
import scribd_helpers
from db_helpers import *

# These are the extensions that can be uploaded to Scribd.com:
ALLOWED_EXTENSIONS = ['txt', 'pdf', 'doc', 'ps', 'rtf', 'epub', 'key', 'odt', 'odp', 'ods', 'odg', 'odf', 'sxw', 'sxc', 'sxi', 'sxd', 'ppt', 'pps', 'xls', 'zip', 'docx', 'pptx', 'ppsx', 'xlsx', 'tif', 'tiff']

# These are the different email notification types that currently exist and are mapped to and from who might receive them and the subject line in /static/json/emails.json
NOTIFICATION_TYPES = ["Request assigned","Question asked",
"Question answered","Request closed","Response added","Request due","Public note added","Request made","Request overdue","Request followed"]


def add_resource(resource, request_body, current_user_id = None):
	fields = request_body.form
	if "extension" in resource:
		return request_extension(int(fields['request_id']), fields.getlist('note_text'), current_user_id)
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
		remove_obj("QA", int(fields['qa_id']))
	elif "qa" in resource:
		return answer_a_question(int(fields['qa_id']), fields['answer_text'])
	elif "owner" in resource:
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

def request_extension(request_id, extension_reasons, user_id):
	update_obj(attribute = "extended", val = True, obj_type = "Request", obj_id = request_id)
	text = "Request extended:"
	for reason in extension_reasons:
		text = text + reason + "</br>"
	add_staff_participant(request_id = request_id, user_id = user_id)
	return add_note(request_id = request_id, text = text, user_id = user_id)

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


def upload_record(request_id, file, description, user_id):
	try:
		doc_id, filename = scribd_helpers.upload_file(file)
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

def add_offline_record(request_id, description, access, user_id):
	record_id = create_record(request_id = request_id, user_id = user_id, access = access, description = description)
	if record_id:
		change_request_status(request_id, "A response has been added.")
		generate_prr_emails(request_id = request_id, notification_type = "City response added")
		add_staff_participant(request_id = request_id, user_id = user_id)
		return record_id
	return False

def add_link(request_id, url, description, user_id):
	record_id = create_record(url = url, request_id = request_id, user_id = user_id, description = description)
	if record_id:
		change_request_status(request_id, "A response has been added.")
		generate_prr_emails(request_id = request_id, notification_type = "City response added")
		add_staff_participant(request_id = request_id, user_id = user_id)
		return record_id
	return False
			
def make_request(text, email = None, assigned_to_name = None, assigned_to_email = None, assigned_to_reason = None, user_id = None, phone = None, alias = None):
	""" Make the request. At minimum you need to communicate which record(s) you want, probably with some text."""
	request_id = find_request(text)
	if not request_id:
		request_id = create_request(text = text, user_id = user_id)
		new_owner_id = assign_owner(request_id = request_id, reason = assigned_to_reason, email = assigned_to_email, alias = assigned_to_name)
		if email: # If the user provided an e-mail address, add them as a subscriber to the request.
			user_id = create_or_return_user(email = email, alias = alias, phone = phone)
			subscriber_id = create_subscriber(request_id = request_id, user_id = user_id)
			generate_prr_emails(request_id, notification_type = "Request made", user_id = subscriber_id)
		open_request(request_id)
		return request_id, True
	return request_id, False

def add_subscriber(request_id, email):
	user_id = create_or_return_user(email = email)
	subscriber_id = create_subscriber(request_id = request_id, user_id = user_id)
	generate_prr_emails(request_id, notification_type = "Request followed", user_id = subscriber_id)

def ask_a_question(request_id, owner_id, question):
	""" City staff can ask a question about a request they are confused about."""
	qa_id = create_QA(request_id = request_id, question = question, owner_id = owner_id)
	if qa_id:
		change_request_status(request_id, "Pending")
		generate_prr_emails(request_id, notification_type = "Question asked", user_id = get_requester(request_id))
		add_staff_participant(request_id = request_id, user_id = get_attribute(attribute = "user_id", obj_id = owner_id, obj_type = "Owner"))
		return qa_id
	return False

def answer_a_question(qa_id, answer, subscriber_id = None):
	""" A requester can answer a question city staff asked them about their request."""
	request_id = create_answer(qa_id, subscriber_id, answer)
	change_request_status(request_id, "Pending")
	generate_prr_emails(request_id = request_id, notification_type = "Question answered")

def open_request(request_id):
	change_request_status(request_id, "Open")


def assign_owner(request_id, reason, email = None, alias = None, phone = None, notify = True): 
	""" Called any time a new owner is assigned. This will overwrite the current owner."""
	user_id = create_or_return_user(email = email, alias = alias, phone = phone)
	req = get_obj("Request", request_id)
	current_owner_id = None
	if not req.current_owner:
		current_owner_id = req.current_owner
	owner_id = find_owner(request_id = int(request_id), user_id = user_id)
	if current_owner_id and owner_id:
		if current_owner_id == owner_id: # This would happen if someone is trying to reassign to the existing owner
			return None 
	new_owner_id = create_owner(request_id = request_id, reason = reason, user_id = user_id)
	update_obj(attribute = "current_owner", val = new_owner_id, obj = req)
	if notify:
		generate_prr_emails(request_id = request_id, notification_type = "Request assigned", user_id = user_id)
	return new_owner_id


def allowed_file(filename):
	ext = filename.rsplit('.', 1)[1]
	return ext in ALLOWED_EXTENSIONS, ext



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

def get_stuff_chrono(stuff, key):
	stuff.sort(key = key)


def set_directory_fields():
	dir_json = open(os.path.join(app.root_path, 'static/json/directory.json'))
	json_data = json.load(dir_json)
	for line in json_data:
		if line['EMAIL_ADDRESS']:
			try:
				last, first = line['FULL_NAME'].split(",")
			except:
				last, junk, first = line['FULL_NAME'].split(",")
			email = line['EMAIL_ADDRESS'].lower()
			user = create_or_return_user(email = email, alias = "%s %s" % (first, last), phone = line['PHONE'], department = line['DEPARTMENT'])

def get_subscriber_attribute(attribute, sid):
	subscriber_user_id = get_attribute(attribute = "user_id", obj_id = sid, obj_type = "Subscriber")
	if subscriber_user_id:
		return get_attribute(attribute = attribute, obj_id = subscriber_user_id, obj_type = "User")
	return None # Requester


def get_requester(request_id): 
# Returns the first person who subscribed to a request, which is the requester
	subscribers = get_attribute(attribute = "subscribers", obj_id = request_id, obj_type = "Request")
	if subscribers:
		subscribers.sort(key = lambda x:x.date_created)
		return get_attribute(attribute = "user_id", obj = subscribers[0])
	return None

def is_request_open(request_id):
	status = get_attribute(attribute = "status", obj_id = request_id, obj_type = "Request")
	if status and 'Closed' in status:
		return False
	return True

def last_note(request_id):
	notes = get_attribute(attribute = "notes", obj_id = request_id, obj_type = "Request")
	if notes:
		return notes[0]
	return None


def close_request(request_id, reason = "", user_id = None):
	req = get_obj("Request", request_id)
	change_request_status(request_id, "Closed")
	# Create a note to capture closed information:
	create_note(request_id, reason, user_id)
	generate_prr_emails(request_id = request_id, notification_type = "Request closed")
	add_staff_participant(request_id = request_id, user_id = user_id)

