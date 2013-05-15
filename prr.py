""" Things one can do relating to a public records request. """

from models import *
import website_copy
import tempfile
import scribd # Used for uploading documents, could use another service
import time
import requests as seaturtle # HTTP requests library, renaming because it's confusing otherwise
import json
from flask import Flask, render_template, request, flash, redirect, url_for
from flask.ext.sqlalchemy import SQLAlchemy, sqlalchemy
from sqlalchemy.exc import IntegrityError, InvalidRequestError
from werkzeug import secure_filename


# Define the local temporary folder where uploads will go
if app.config['PRODUCTION']:
	UPLOAD_FOLDER = app.config['UPLOAD_FOLDER']
else:
	UPLOAD_FOLDER = "%s/uploads" % os.getcwd()
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'doc', 'ps', 'rtf', 'epub', 'key', 'odt', 'odp', 'ods', 'odg', 'odf', 'sxw', 'sxc', 'sxi', 'sxd', 'ppt', 'pps', 'xls', 'zip', 'docx', 'pptx', 'ppsx', 'xlsx', 'tif', 'tiff'])

def get_resource(resource, url, resource_id):
	headers = {'content-type': 'application/json; charset=utf-8'}
	r = seaturtle.get("%s/api/%s/%s" %(url, resource, resource_id), headers=headers)
	if r:
		return r.json()
	return None

def get_resources(resource, url):
	headers = {'content-type': 'application/json; charset=utf-8'}
	r = seaturtle.get("%s/api/%s" %(url, resource), headers=headers)
	if r:
		return r.json()
	return None

def add_resource(resource, request_body):
	fields = request_body.form
	if "note" in resource:
		add_note(fields['request_id'], fields['note_text'], fields['current_owner'])
	elif "record" in resource:
		upload_record(fields['request_id'], request.files['record'], fields['record_description'])
	elif "link" in resource:
		add_link(fields['request_id'], fields['record_url'], fields['record_description'])
	elif "qa" in resource:
		owner_id = None #TODO: get logged in user
		ask_a_question(fields['request_id'], owner_id, fields['question'])
	else:
		return False
	return True

def add_note(request_id, text, owner_id):
	note = Note(request_id = request_id, text = text, owner_id = owner_id)
	db.session.add(note)
	db.session.commit()
	change_request_status(request_id, "A response has been added.")


def upload_record(request_id, file, description):
	doc_id, filename = upload_file(file)
	req = get_resource("request", app.config['APPLICATION_URL'], request_id)
	if str(doc_id).isdigit():
		record = Record(doc_id = doc_id, request_id = request_id, owner_id = req['current_owner'], description = description)
		db.session.add(record)
		db.session.commit()
		record.filename = filename
		record.url = app.config['HOST_URL'] + doc_id
		db.session.commit()
		change_request_status(request_id, "A response has been added.")
	else:
		return "Not an allowed doc type"

def add_link(request_id, url, description):
	req = get_resource("request", app.config['APPLICATION_URL'], request_id)
	record = Record(url = url, request_id = request_id, owner_id = req['current_owner'], description = description)
	db.session.add(record)
	db.session.commit()
	change_request_status(request_id, "A response has been added.")
			

def make_request(text, email = None, assigned_to_name = None, assigned_to_email = None, assigned_to_reason = None):
	""" Make the request. At minimum you need to communicate which record(s) you want, probably with some text."""
	req = Request.query.filter_by(text = text).first()
	if not req:
		req = Request(text)
		db.session.add(req)
		db.session.commit()
		past_owner_id, owner_id = assign_owner(request_id = req.id, reason = assigned_to_reason, email = assigned_to_email, alias = assigned_to_name)
		if email: # If the user provided an e-mail address, add them as a subscriber to the request.
			user = create_or_return_user(email = email)
			subscriber = Subscriber(request_id = req.id, user_id = user.id)
			db.session.add(subscriber)
			db.session.commit()
		open_request(req.id)
		return req.id, True
	return req.id, False

def ask_a_question(request_id, owner_id, question):
	""" City staff can ask a question about a request they are confused about."""
	qa = QA(request_id = request_id, question = question)
	qa.owner_id = owner_id
	db.session.add(qa)
	db.session.commit()
	change_request_status(request_id, "Pending")
	return qa.id

def answer_a_question(qa_id, subscriber_id, answer):
	""" A requester can answer a question city staff asked them about their request."""
	qa = QA.query.get(qa_id) 
	qa.subscriber_id = subscriber_id
	qa.answer = answer
	db.session.add(qa)
	db.session.commit()
	change_request_status(qa.request_id, "Pending")
	# change_request_status(request_id, "%s needs to take action." %) # Pass the buck to the current owner

def create_or_return_user(email, alias = None):
	user = User.query.filter_by(email = email).first()
	if not user:
		user = User(email = email, alias = alias)
		db.session.add(user)
		db.session.commit()
	return user

def open_request(id):
	change_request_status(id, "Open")

def close_request(id, reason = ""):
	change_request_status(id, "Closed. %s" %reason)

def get_user(email):
	user = User.query.filter_by(email = email).first()
	return user

def assign_owner(request_id, reason, email = None, alias = None): 
	""" Called any time a new owner is assigned. This will overwrite the current owner."""
	user = create_or_return_user(email = email, alias = alias)
	req = Request.query.get(request_id)
	current_owner_id = req.current_owner
	owner = Owner.query.filter_by(request_id = request_id, user_id = user.id).first()
	if current_owner_id and owner:
		if current_owner_id == owner.id:
			return None, None
	owner = Owner(request_id = request_id, user_id = user.id, reason = reason)
	db.session.add(owner)
	db.session.commit()
	if current_owner_id:
		past_owner_id = current_owner_id
	else:
		past_owner_id = None
	req.current_owner = owner.id
	db.session.commit()
	change_request_status(request_id, "Assigned to %s" % email)
	return past_owner_id, owner.id

def remove_subscriber(subscriber_id): 
	try:
		subscriber = Subscriber.query.get(subscriber_id)
		db.session.delete(subscriber)
		db.session.commit()
		return True # removed successfully
	except:
		return False 

def change_request_status(id, status):
	try:
		req = Request.query.get(id)
		req.status = status
		req.status_updated = datetime.now()
		db.session.commit()
		return True
	except:
		return False

def progress(bytes_sent, bytes_total):
    print("%s of %s (%s%%)" % (bytes_sent, bytes_total, bytes_sent*100/bytes_total))

def upload(filepath, API_KEY, API_SECRET):
    # Configure the Scribd API.
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

def upload_file(file): 
# Uploads file to scribd.com and returns doc ID. File can be accessed at scribd.com/doc/id
	if file and allowed_file(file.filename):
		filename = secure_filename(file.filename)
		filepath = os.path.join(UPLOAD_FOLDER, filename)
		file.save(filepath)
		doc_id = upload(filepath, app.config['SCRIBD_API_KEY'], app.config['SCRIBD_API_SECRET'])
		return doc_id, filename
	return None, None
