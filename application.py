import os
from werkzeug import secure_filename
from flask import Flask, render_template, request, flash, redirect, url_for
from upload import upload
from flask.ext.sqlalchemy import SQLAlchemy, sqlalchemy
from sqlalchemy.exc import IntegrityError, InvalidRequestError
from flask.ext.mail import Mail
from flask.ext.mail import Message
import website_copy
# from notifications import *
UPLOAD_FOLDER = "%s/uploads" % os.getcwd()
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'doc'])
app = Flask(__name__)
db = SQLAlchemy(app)
db.create_all()
from models import *
config = os.path.join(app.root_path, 'settings.cfg')
app.config.from_pyfile(config)
mail = Mail(app)


def send_email(body, recipients = ["richa.agarwal85@gmail.com"], subject = "No subject"):
	message = Message(subject, recipients, sender = app.config['DEFAULT_MAIL_SENDER'])
	message.html = body
	mail.send(message)

@app.route('/test')
def sandbox():
	return render_template('test.html')

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
		return doc_id
	return None


@app.route('/upload', methods=['GET', 'POST'])
def load():
	if request.method == 'POST':
		doc_id = -1
		file = request.files['record']
		if upload_file(file) != None:
			try:
				request_id = request.form['request_id']
				email = "citystaff@oakland.net"
				alias = "city staff"
				owner = Owner(email = email, alias = alias)
				# Realistically we would get owner ID some other way and not create a new owner/subscriber
				db.session.add(owner)
				db.session.commit()
				subscriber = Subscriber(request_id = request_id, email = email, alias = alias )
				subscriber.owner_id = owner.id
				db.session.add(subscriber)
				db.session.commit()
				record = Record(doc_id, request_id, owner.id)
				db.session.add(record)
				db.session.commit()
				return render_template('uploaded.html', doc_id = doc_id, request_id = request_id)
			except:
				return render_template('error.html', message = doc_id)
		else:
			return render_template('error.html', message = "Not an allowed doc type")

@app.route('/city/request/<int:request_id>')
def show_request_for_city(request_id):
	return render_template('manage_request_City.html')

@app.route('/request/<int:request_id>')
def show_request(request_id):
    # show the request with the given id, the id is an integer
    r = Request.query.get(request_id)
    doc_ids = []
    owner_emails = []
    owners = get_owners(request_id)
    if owners:
    	for owner in owners:
    		owner_emails.append(Owner.query.get(owner).email)
    if r.records:
    	for record in r.records:
    		if record.scribd_id:
    			doc_ids.append(record.scribd_id)
    		else:
    			doc_ids.append("Nothing uploaded yet by %s" % owner.name)
    return render_template('case.html', text = r.text, request_id = request_id, doc_ids = doc_ids, status = r.status, owner_emails = owner_emails)


def assign_owner(request_id, alias, email):
	owner = Owner(alias = alias, email = email)
	db.session.add(owner)
	db.session.commit()
	subscriber = Subscriber(request_id = request_id, alias = alias, email = email)
	subscriber.owner_id = owner.id
	db.session.add(subscriber)
	db.session.commit()
	return owner.id

def unassign_owner(subscriber_id):
	subscriber = Subscriber.query.get(subscriber_id)
	if subscriber.owner_id:
		owner = Owner.query.get(subscriber.owner_id)
		db.session.delete(owner)
		db.session.commit()
		return True # Unassigned successfully
	return False # No one to unassign

def make_request(str, email = None):
	try:
		req = Request(str)
		db.session.add(req)
		db.session.commit()
		owner_id = assign_owner(req.id, app.config['DEFAULT_OWNER_NAME'], app.config['DEFAULT_OWNER_EMAIL'])
		if email: # If the user provided an e-mail address, add them as a subscriber to the request.
			subscriber = Subscriber(req.id, email)
			db.session.add(subscriber)
			db.session.commit()
		open_request(req.id)
		db.session.commit()
		return req.id
	except IntegrityError:
		return None

def change_request_status(id, status):
	try:
		req = Request.query.get(id)
		req.status = status
		db.session.commit()
		return True
	except:
		return False

def get_owners(request_id):
	req = Request.query.get(request_id)
	subscribers = req.subscribers
	for subscriber in subscribers:
		if subscriber.owner_id != None:
			yield subscriber.owner_id

def notify(request_id):
	req = Request.query.get(request_id)
	subscribers = req.subscribers
	owner_emails = []
	for owner_id in get_owners(req.id):
		email = Owner.query.get(owner_id).email
		owner_emails.append(email)
	city_subject, city_body = website_copy.request_submitted_city(req.text)
	public_subject, public_body = website_copy.request_submitted(req.text, owner_emails, "510-555-1022") 
	if len(subscribers) != 0:
		for subscriber in subscribers:
			if subscriber.owner_id:
				send_email(body = city_body, recipients = [subscriber.email], subject = city_subject)
			else:
				send_email(body = public_body, recipients = [subscriber.email], subject = public_subject)
	else:
		print "No one assigned!"


def open_request(id):
	change_request_status(id, "Open")
	notify(id)

def close_request(id, reason = ""):
	change_request_status(id, "Closed. %s" %reason)
	notify(id)


@app.route('/', methods=['GET', 'POST'])
def new_request():
	if request.method == 'POST':
		request_text = request.form['request_text']
		email = request.form['request_email']
		request_id = make_request(request_text, email)
		if request_id:
			return show_request(request_id)
		else:
			db.session.rollback()
			req = Request.query.filter_by(text = request_text).first()
			return render_template('error.html', message = "Your request is the same as /request/%s" % req.id)
	return render_template('new_request.html')

@app.route('/requests', methods=['GET', 'POST'])
def requests():
	all_record_requests = Request.query.all()
	return render_template('all_requests.html', all_record_requests = all_record_requests)

if __name__ == '__main__':
	app.run(use_debugger=True, debug=True)

