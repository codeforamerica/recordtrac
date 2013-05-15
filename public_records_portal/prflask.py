from flask import render_template, request, flash, redirect, url_for
from flask.ext.login import LoginManager, login_user, logout_user, current_user, login_required
from sqlalchemy.exc import IntegrityError, InvalidRequestError
from public_records_portal import app, filters, prr
from filters import *
from prr import *
import json
import sendgrid
import os


# Initialize login
login_manager = LoginManager()
login_manager.init_app(app)

mail = sendgrid.Sendgrid(app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'], secure = True)

NOTIFICATIONS = [
					   # 'note', 
					   # 'new', 
					   # 'close',                                      
					   # 'reroute',                                     
					   # 'record',
					   # 'link',
					   # 'qa'
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
		request_id, is_new = make_request(text = request_text, email = email, assigned_to_name = app.config['DEFAULT_OWNER_NAME'], assigned_to_email = app.config['DEFAULT_OWNER_EMAIL'], assigned_to_reason = app.config['DEFAULT_OWNER_REASON'])
		if is_new:
			# send_emails(body = show_request(request_id, for_email_notification = True), request_id = request_id, notification_type = "new")
			return show_request(request_id, "requested.html")
		return render_template('error.html', message = "Your request is the same as /request/%s" % request_id)
	return render_template('new_request.html')

# Uploading a record is specific to a case, so this only gets called from a case (that only city staff have a view of)
@app.route('/upload', methods=['POST'])
def load():
	if request.method == 'POST':


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
			past_owner_id, current_owner_id = assign_owner(request_id = request_id, reason = reason, email = owner_email)
			past_owner = None
			if past_owner_id:
				past_owner = get_resource("owner", app.config['APPLICATION_URL'], past_owner_id)
			if current_owner_id:
				send_emails(body = show_request(request_id, for_email_notification = True), request_id = request_id, notification_type = "reroute", past_owner = past_owner)
			else:
				print "Can't reassign to same owner." #TODO: Do we need to convey this to the user?
	return show_request(request_id = request_id, template = "manage_request_%s.html" %(audience))

@app.route('/request/<int:request_id>')
def show_request(request_id, template = None, record_uploaded = None, for_email_notification = False):
	if not template:
		template = "case.html"
	req = get_resource("request", app.config['APPLICATION_URL'], request_id)
	if not req:
		return render_template('error.html', message = "A request with ID %s does not exist." % request_id)
	if "Closed" in req['status']:
		template = "closed.html"
	return render_template(template, req = req, for_email_notification = for_email_notification, record_uploaded = record_uploaded)
@app.route('/add_a_<string:resource>', methods=['GET', 'POST'])
def add_a_resource(resource):
	if request.method == 'POST':
		add_resource(resource, request)
		send_emails(body = show_request(request.form['request_id'], for_email_notification = True), request_id = request.form['request_id'], notification_type = resource)
		return show_request(request.form['request_id'], template = "manage_request_city.html")
	return render_template('error.html', message = "You can only add a %s from a request page!" %resource)
		
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
		close_request(request_id, request.form['reason'])
		send_emails(body = show_request(request_id, for_email_notification = True), request_id = request_id, notification_type = "close")
		return show_request(request_id, template= template)
	return render_template('error.html', message = "You can only close from a requests page!")


# Shows all public records requests that have been made.
@app.route('/requests')
def requests():
	all_record_requests = get_resources("request", app.config['APPLICATION_URL'])
	if all_record_requests:
		return render_template('all_requests.html', all_record_requests = all_record_requests['objects'])
	return index()

# Shows all public records requests that have been made by current owner. This doesn't work currently.
@app.route('/your_requests')
@login_required
def your_requests():
	all_record_requests = []
	owners = Owner.query.filter_by(user_id = current_user.id) # TODO: Make API call instead
	for owner in owners:
		req = Request.query.filter_by(current_owner = owner.id) # TODO: Make API call instead
		all_record_requests.append(req)
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

@login_manager.user_loader
def load_user(userid):
	user = User.query.get(userid)
	return user

@app.route("/login", methods=["GET", "POST"])
def login(email):
	user = create_or_return_user(email=email)
	login_user(user)
	return index()

@app.route("/logout")
@login_required
def logout():
	logout_user()
	return index()

# Functions that should probably go somewhere else:


def send_email(body, recipient, subject):
	sender = app.config['DEFAULT_MAIL_SENDER']
	plaintext = ""
	html = body
	message = sendgrid.Message(sender, subject, plaintext, html)
	message.add_to(recipient)
	# message.add_bcc(sender)
	mail.web.send(message)

def send_emails(body, request_id, notification_type, past_owner = None):
	city_page = "%scity/request/%s" %(app.config['APPLICATION_URL'],request_id)
	public_page = "%srequest/%s" %(app.config['APPLICATION_URL'],request_id)
	req = get_resource("request", app.config['APPLICATION_URL'], request_id)
	if notification_type in NOTIFICATIONS:
		owner = get_resource("owner", app.config['APPLICATION_URL'], req['current_owner'])
		subject_subscriber = ""
		subject_owner = ""
		user = get_resource("user", app.config['APPLICATION_URL'], owner['user_id'])
		owner_email = user['email']
		past_owner_email = None
		if past_owner:
			past_owner_user = get_resource("user", app.config['APPLICATION_URL'], past_owner['user_id'])
			past_owner_email = past_owner_user['email']
		if notification_type == 'new':
			send_to_owner, send_to_subscribers = True, False
			subject_subscriber, additional_body = website_copy.request_submitted("", "", "")
			subject_owner, additional_body = website_copy.request_submitted_city("")
		elif notification_type == 'note':
			send_to_owner, send_to_subscribers = False, True
			subject_subscriber, subject_owner = website_copy.note_added(owner_email)
		elif notification_type == 'record':
			send_to_owner, send_to_subscribers = False, True
			subject_subscriber, subject_owner = website_copy.record_added(owner_email)
		elif notification_type == 'close':
			send_to_owner, send_to_subscribers = False, True
			subject_subscriber = "Your request has been closed."
		elif notification_type == 'reroute':
			send_to_owner, send_to_subscribers = True, False
			subject_subscriber, subject_owner = website_copy.request_routed(past_owner_email)
		if send_to_subscribers:
			for subscriber in req.subscribers:
				subscriber_user = get_resource("user", app.config['APPLICATION_URL'], subscriber['user_id'])
				subscriber_email = subscriber_user['email']
				email_body = "View this request: %s </br> %s" % (public_page, body)
				send_email(email_body, subscriber_email,subject_subscriber)
		if send_to_owner:
			email_body = "View and manage this request: %s </br> %s" %(city_page, body)
			send_email(email_body.as_string(), owner_email, subject_owner)
	else:
		print 'Not a valid notification type.'
