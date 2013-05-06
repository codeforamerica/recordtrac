import os
from werkzeug import secure_filename
from flask import Flask, render_template, request, flash, redirect, url_for
from flask.ext.sqlalchemy import SQLAlchemy, sqlalchemy
from sqlalchemy.exc import IntegrityError, InvalidRequestError
from datetime import datetime
import json
import sendgrid

# Initialize Flask app and database:
app = Flask(__name__)
db = SQLAlchemy(app)
db.create_all()

from prr import *

# Get configuration settings from settings.cfg
config = os.path.join(app.root_path, 'settings.cfg')
app.config.from_pyfile(config) 

# Get filepath for actions.json
actions_filepath = os.path.join(app.root_path, 'actions.json')
mail = sendgrid.Sendgrid(app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'], secure = True)


# Define the local temporary folder where uploads will go
if app.config['PRODUCTION']:
	UPLOAD_FOLDER = app.config['UPLOAD_FOLDER']
else:
	UPLOAD_FOLDER = "%s/uploads" % os.getcwd()
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'doc', 'ps', 'rtf', 'epub', 'key', 'odt', 'odp', 'ods', 'odg', 'odf', 'sxw', 'sxc', 'sxi', 'sxd', 'ppt', 'pps', 'xls', 'zip', 'docx', 'pptx', 'ppsx', 'xlsx', 'tif', 'tiff'])
NOTIFICATIONS = [
	                   # 'note', 
	                   # 'new', 
	                   # 'close',                                      
	                   # 'reroute',                                     
	                   # 'record'
				]

# Routing

# Let's start with the index page! For now we'll let the users submit a new request.
@app.route('/', methods=['GET', 'POST'])
def index():
	return new_request()

@app.route('/actions')
def explain_all_actions():
	action_json = open('actions.json')
	json_data = json.load(action_json)
	actions = []
	for data in json_data:
		actions.append("%s: %s" %(data, json_data[data]))
	return render_template('actions.html', actions = actions)

# They can always submit a new request by navigating here, but the index might change.
@app.route('/new', methods=['GET', 'POST'])
def new_request():
	if request.method == 'POST':
		request_text = request.form['request_text']
		email = request.form['request_email']
		try:
			request_id = make_request(request_text, email, app.config['DEFAULT_OWNER_NAME'], app.config['DEFAULT_OWNER_EMAIL'], app.config['DEFAULT_OWNER_REASON'])
		except IntegrityError:
			return None
		if request_id:
			send_emails(body = show_request(request_id, for_email_notification = True), request_id = request_id, notification_type = "new")
			return show_request(request_id, "requested.html")
		else:
			db.session.rollback()
			req = Request.query.filter_by(text = request_text).first()
			return render_template('error.html', message = "Your request is the same as /request/%s" % req.id)
	return render_template('new_request.html')

# Uploading a record is specific to a case, so this only gets called from a case (that only city staff have a view of)
@app.route('/upload', methods=['POST'])
def load():
	if request.method == 'POST':
		description = request.form['record_description']
		request_id = request.form['request_id']
		req = Request.query.get(request_id)
		owner_id = req.current_owner
		record = None
		if 'record_url' in request.form: # If they're just pointing to a URL where the document already exists
			url = request.form['record_url']
			record = Record(url = url, request_id = request_id, owner_id = owner_id, description = description)
			db.session.add(record)
		else:
			file = request.files['record']
			doc_id, filename = upload_file(file)
			if str(doc_id).isdigit():
				record = Record(doc_id = doc_id, request_id = request_id, owner_id = owner_id, description = description)
				db.session.add(record)
				db.session.commit()
				record.filename = filename
				record.url = app.config['HOST_URL'] + doc_id
			else:
				return render_template('error.html', message = "Not an allowed doc type")
		db.session.commit()
		send_emails(body = show_request(request_id, for_email_notification = True), request_id = request_id, notification_type = "record")
		return show_request(request_id = request_id, template = "uploaded.html", record_uploaded = record)
	return render_template('error.html', message = "You can only upload from a requests page!")


# Returns a view of the case based on the audience. Currently views exist for city staff or general public.
@app.route('/<string:audience>/request/<int:request_id>', methods=['GET', 'POST'])
def show_request_for_x(audience, request_id):
	if request.method == 'POST':
		owner_email = request.form['owner_email']
		owner_reason = request.form['owner_reason']
		if owner_email:
			reason = ""
			if owner_reason:
				reason = owner_reason
			past_owner_id, current_owner_id = assign_owner(request_id, "", owner_email, reason)
			past_owner = Owner.query.get(past_owner_id)
			send_emails(body = show_request(request_id, for_email_notification = True), request_id = request_id, notification_type = "reroute", past_owner = past_owner)
	return show_request(request_id = request_id, template = "manage_request_%s.html" %(audience))

@app.route('/request/<int:request_id>')
def show_request(request_id, template = "case.html", record_uploaded = None, for_email_notification = False):
    req = get_request(request_id = request_id, url = app.config['APPLICATION_URL'])
    if not req:
    	return render_template('error.html', message = "A request with ID %s does not exist." % request_id)
    doc_ids = []
    owner = Owner.query.get(req['current_owner'])
    if "Closed" in req['status']:
    	template = "closed.html"
    requester = get_requester(request_id)
    requester_email = None
    if requester:
    	requester_email = requester.email
    return render_template(template, text = req['text'], request_id = request_id, records = req['records'], status = req['status'], owner = owner, date = owner.date_created.date(), date_updated = req['status_updated'], record_uploaded = record_uploaded, notes = req['notes'], requester_email = requester_email, for_email_notification = for_email_notification)

@app.route('/note', methods=['POST'])
def add_note():
	if request.method == 'POST':
		request_id = request.form['request_id']
		req = Request.query.get(request_id)
		note = Note(request_id = req.id, text = request.form['note_text'], owner_id = req.current_owner)
		db.session.add(note)
		db.session.commit()
		send_emails(body = show_request(request_id, for_email_notification = True), request_id = request_id, notification_type = "note")
		return show_request(request_id, template = "manage_request_city.html")
	return render_template('error.html', message = "You can only add a note from a requests page!")

# Clears/updates tables in the database until I figure out how I want to deal with migrations
@app.route('/clear')
def clear_db():
	message = "You can't do that here."
	if not app.config['PRODUCTION']:
		try:
			db.session.commit()
			db.drop_all()
			db.create_all()
			db.session.commit()
			return requests()
		except:
			message = "Dropping the tables didn't work :("
	return render_template('error.html', message = message)

# Closing is specific to a case, so this only gets called from a case (that only city staff have a view of)
@app.route('/close', methods=['POST'])
def close(request_id = None):
	if request.method == 'POST':
		template = 'closed.html'
		request_id = request.form['request_id']
		req = Request.query.get(request_id)
		subscribers = req.subscribers
		close_request(request_id, request.form['reason'])
		send_emails(body = show_request(request_id, for_email_notification = True), request_id = request_id, notification_type = "close")
		return show_request(request_id, template= template)
	return render_template('error.html, message = "You can only close from a requests page!')


# Shows all public records requests that have been made.
@app.route('/requests')
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
		return doc_id, filename
	return None, None


def send_email(body, recipient, subject):
	sender = app.config['DEFAULT_MAIL_SENDER']
	plaintext = ""
	html = body
	message = sendgrid.Message(sender, subject, plaintext, html)
	message.add_to(recipient)
	message.add_bcc(sender)
	mail.web.send(message)

def send_emails(body, request_id, notification_type, past_owner = None):
	city_page = "%scity/request/%s" %(app.config['APPLICATION_URL'],request_id)
	public_page = "%srequest/%s" %(app.config['APPLICATION_URL'],request_id)
	req = Request.query.get(request_id)
	if notification_type in NOTIFICATIONS:
		owner = Owner.query.get(req.current_owner)
		subject_subscriber = ""
		subject_owner = ""
		if notification_type == 'new':
			send_to_owner, send_to_subscribers = True, False
			subject_subscriber, additional_body = website_copy.request_submitted("", "", "")
			subject_owner, additional_body = website_copy.request_submitted_city("")
		elif notification_type == 'note':
			send_to_owner, send_to_subscribers = False, True
			subject_subscriber, subject_owner = website_copy.note_added(owner.email)
		elif notification_type == 'record':
			send_to_owner, send_to_subscribers = False, True
			subject_subscriber, subject_owner = website_copy.record_added(owner.email)
		elif notification_type == 'close':
			send_to_owner, send_to_subscribers = False, True
			subject_subscriber = "Your request has been closed."
		elif notification_type == 'reroute':
			send_to_owner, send_to_subscribers = True, False
			subject_subscriber, subject_owner = website_copy.request_routed(past_owner.email)
		if send_to_subscribers:
			for subscriber in req.subscribers:
				if subscriber.email:
					send_email("View this request: " + public_page + "</br>" + body, subscriber.email, subject_subscriber)
		if send_to_owner:
			send_email("View and manage this request: " + city_page + "</br>" + body, owner.email, subject_owner)
	else:
		print 'Not a valid notification type.'

def get_requester(request_id):
	req = Request.query.get(request_id)
	for subscriber in req.subscribers:
		if subscriber.creator:
			return subscriber
	return None


# Filters

@app.template_filter('date')
def date(obj):
	try:
		return obj.date()
	except:
		return time.strptime(obj, '%Y-%m-%d')

@app.template_filter('owner_name')
def owner_name(oid):
	owner = Owner.query.get(oid)
	if owner.alias:
		return owner.alias
	return owner.email

@app.template_filter('explain_action')
def explain_action(action):
	action_json = open(actions_filepath)
	json_data = json.load(action_json)
	return json_data[action]



if __name__ == '__main__':
	app.run(use_debugger=True, debug=True)

