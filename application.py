import os
from werkzeug import secure_filename
from flask import Flask, render_template, request, flash, redirect, url_for
from flask.ext.sqlalchemy import SQLAlchemy, sqlalchemy
from sqlalchemy.exc import IntegrityError, InvalidRequestError
from flask.ext.mail import Mail, Message
from upload import upload
import website_copy
from datetime import datetime

# Initialize Flask app and database:
app = Flask(__name__)
db = SQLAlchemy(app)
db.create_all()
from models import *

# Get configuration settings from settings.cfg
config = os.path.join(app.root_path, 'settings.cfg')
app.config.from_pyfile(config) 

mail = Mail(app)

# Define the local temporary folder where uploads will go
UPLOAD_FOLDER = "%s/uploads" % os.getcwd()
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'doc'])

# Routing

# Let's start with the index page! For now we'll let the users submit a new request.
@app.route('/', methods=['GET', 'POST'])
def index():
	return new_request()

# They can always submit a new request by navigating here, but the index might change.
@app.route('/new', methods=['GET', 'POST'])
def new_request():
	if request.method == 'POST':
		request_text = request.form['request_text']
		email = request.form['request_email']
		request_id = make_request(request_text, email)
		if request_id:
			return show_request(request_id, "requested.html")
		else:
			db.session.rollback()
			req = Request.query.filter_by(text = request_text).first()
			return render_template('error.html', message = "Your request is the same as /request/%s" % req.id)
	return render_template('new_request.html')

# Uploading is specific to a case, so this only gets called from a case (that only city staff have a view of)
@app.route('/upload', methods=['POST'])
def load():
	if request.method == 'POST':
		doc_id = -1
		file = request.files['record']
		doc_id = upload_file(file)
		if doc_id != None:
			try:
				request_id = request.form['request_id']
				req = Request.query.get(request_id)
				owner_id = req.current_owner
				record = Record(scribd_id = doc_id, request_id = request_id, owner_id = owner_id, description = "")
				db.session.add(record)
				db.session.commit()
				return show_request(request_id, template = "uploaded.html")
			except:
				return render_template('error.html', message = doc_id)
		else:
			return render_template('error.html', message = "Not an allowed doc type")
	return render_template('error.html', message = "You can only upload from a requests page!")

# Returns a view of the case based on the audience. Currently views exist for city staff or general public.
@app.route('/<string:audience>/request/<int:request_id>')
def show_request_for_x(audience, request_id):
	return show_request(request_id = request_id, template = "manage_request_%s.html" %(audience))

@app.route('/request/<int:request_id>')
def show_request(request_id, template = "case.html"):
    # show the request with the given id, the id is an integer
    req = Request.query.get(request_id)
    doc_ids = []
    owner = Owner.query.get(req.current_owner)
    owner_email = owner.email
    if req.records:
    	for record in req.records:
    		if record.scribd_id:
    			doc_ids.append(record.scribd_id)
    		else:
    			doc_ids.append("Nothing uploaded yet by %s" % owner.name)
    return render_template(template, text = req.text, request_id = request_id, doc_ids = doc_ids, status = req.status, owner_email = owner_email, date = owner.date_created.date())

# Shows all public records requests that have been made.
@app.route('/requests', methods=['GET', 'POST'])
def requests():
	all_record_requests = Request.query.all()
	return render_template('all_requests.html', all_record_requests = all_record_requests)


# test template:  I clearly don't know what should go here, but need to keep a testbed here.
@app.route('/test')
def show_test():
	return render_template('test.html')

@app.route('/<string:page>')
def any_page(page):
	try:
		return render_template('%s.html' %(page))
	except:
		return render_template('error.html', message = "%s totally doesn't exist." %(page))

# Functions that should probably go somewhere else:

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

def open_request(id):
	change_request_status(id, "Open")
	notify(id)

def close_request(id, reason = ""):
	change_request_status(id, "Closed. %s" %reason)
	notify(id)

def assign_owner(request_id, alias, email): 
# Called any time a new owner is assigned. This will overwrite the current owner.
	owner = Owner(alias = alias, request_id = request_id, email = email)
	db.session.add(owner)
	db.session.commit()
	req = Request.query.get(request_id)
	req.current_owner = owner.id
	db.session.commit()
	return owner.id

def remove_subscriber(subscriber_id): 
	try:
		subscriber = Subscriber.query.get(subscriber_id)
		db.session.delete(subscriber)
		db.session.commit()
		return True # Unassigned successfully
	except:
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

def notify(request_id):
	req = Request.query.get(request_id)
	subscribers = req.subscribers
	owner = Owner.query.get(req.current_owner)
	city_subject, city_body = website_copy.request_submitted_city(req.text)
	public_subject, public_body = website_copy.request_submitted(req.text, owner.email, "xxx-xxx-xxxx")
	send_email(body = city_body, recipients = [owner.email], subject = city_subject) 
	if len(subscribers) != 0:
		for subscriber in subscribers:
			send_email(body = public_body, recipients = [subscriber.email], subject = public_subject)
	else:
		print "No one assigned!"

def send_email(body, recipients, subject):
	message = Message(subject, recipients, sender = app.config['DEFAULT_MAIL_SENDER'])
	message.html = body
	mail.send(message)

if __name__ == '__main__':
	app.run(use_debugger=True, debug=True)

