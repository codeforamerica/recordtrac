""" Things one can do relating to a public records request. """

from models import *
import prflask
from prflask import db
import website_copy
import tempfile
import scribd # Used for uploading documents, could use another service
import time
import requests as seaturtle
import json

def get_request(request_id, url):
	headers = {'content-type': 'application/json; charset=utf-8'}
	r = seaturtle.get("%s/api/request/%s" %(url, request_id), headers=headers)
	return r.json()

def make_request(str, email = None, assigned_to_name = None, assigned_to_email = None, assigned_to_reason = None):
	""" Make the request. At minimum you need to communicate which record(s) you want, probably with some text."""
	req = Request(str)
	db.session.add(req)
	db.session.commit()
	owner_id = assign_owner(req.id, assigned_to_name, assigned_to_email, assigned_to_reason)
	if email: # If the user provided an e-mail address, add them as a subscriber to the request.
		subscriber = Subscriber(req.id, email)
		db.session.add(subscriber)
		db.session.commit()
	open_request(req.id)
	db.session.commit()
	return req.id

def open_request(id):
	change_request_status(id, "Open")
	# notify(id)

def close_request(id, reason = ""):
	change_request_status(id, "Closed. %s" %reason)
	# notify(id)

def assign_owner(request_id, alias, email, reason): 
	""" Called any time a new owner is assigned. This will overwrite the current owner."""
	owner = Owner(alias = alias, request_id = request_id, email = email, reason = reason)
	db.session.add(owner)
	db.session.commit()
	req = Request.query.get(request_id)
	past_owner_id = req.current_owner
	req.current_owner = owner.id
	db.session.commit()
	return past_owner_id, owner.id

def remove_subscriber(subscriber_id): 
	try:
		subscriber = Subscriber.query.get(subscriber_id)
		db.session.delete(subscriber)
		db.session.commit()
		return True # Unassigned successfully
	except:
		return False # No one to unassign

def change_request_status(id, status):
	try:
		req = Request.query.get(id)
		req.status = status
		req.status_updated = datetime.now()
		db.session.commit()
		return True
	except:
		return False


def notify(request_id):
	req = Request.query.get(request_id)
	subscribers = req.subscribers
	owner = Owner.query.get(req.current_owner)
	city_subject, city_body = website_copy.request_submitted_city(req.text)
	public_subject, public_body = website_copy.request_submitted(req.text, owner.email, "xxx-xxx-xxxx")
	prflask.send_email(body = city_body, recipients = [owner.email], subject = city_subject) 
	if len(subscribers) != 0:
		for subscriber in subscribers:
			prflask.send_email(body = public_body, recipients = [subscriber.email], subject = public_subject)
	else:
		print "No one assigned!"

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