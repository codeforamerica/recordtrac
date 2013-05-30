from flask import render_template, request, flash, redirect, url_for
from flask.ext.login import LoginManager, login_user, logout_user, current_user, login_required
from sqlalchemy.exc import IntegrityError, InvalidRequestError
from public_records_portal import app, filters, prr, models
from filters import *
from prr import *
import json
import os

# Initialize login
login_manager = LoginManager()
login_manager.init_app(app)


# Routing

# Let's start with the index page! For now we'll let the users submit a new request.
@app.route('/', methods = ['GET', 'POST'])
def index():
	return new_request()

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.route('/actions')
def explain_all_actions():
	action_json = open(os.path.join(app.root_path, 'actions.json'))
	json_data = json.load(action_json)
	actions = []
	for data in json_data:
		actions.append("%s: %s" %(data, json_data[data]))
	return render_template('actions.html', actions = actions)

# They can always submit a new request by navigating here, but the index might change.
@app.route('/new', methods=['GET','POST'])
def new_request():
	current_user_id = None
	if current_user.is_anonymous() == False:
		current_user_id = current_user.id
	if request.method == 'POST':
		request_text = request.form['request_text']
		email = request.form['request_email']
		alias = None
		phone = None
		if 'request_alias' in request.form:
			alias = request.form['request_alias']
		if 'request_phone' in request.form:
			phone = request.form['request_phone']
		request_id, is_new = make_request(text = request_text, email = email, assigned_to_name = app.config['DEFAULT_OWNER_NAME'], assigned_to_email = app.config['DEFAULT_OWNER_EMAIL'], assigned_to_reason = app.config['DEFAULT_OWNER_REASON'], user_id = current_user_id, alias = alias, phone = phone)
		if is_new:
			# return redirect(url_for('show_request', request_id = request_id, banner_msg = "Thanks! Your request has been uploaded.", template = "requested.html"))
			return show_request(request_id, banner_msg = "Thanks! Your request has been uploaded.", template = "requested.html")
		return render_template('error.html', message = "Your request is the same as /request/%s" % request_id)
	else:
		return render_template('new_request.html', user_id = current_user_id)

# Returns a view of the case based on the audience. Currently views exist for city staff or general public.
@app.route('/<string:audience>/request/<int:request_id>', methods=['GET', 'POST'])
@login_required
def show_request_for_x(audience, request_id):
	if request.method == 'POST':
		owner_email = request.form['owner_email']
		owner_reason = request.form['owner_reason']
		assign_owner(request_id = request_id, reason = owner_reason, email = owner_email)
	return show_request(request_id = request_id, template = "manage_request_%s.html" %(audience))

@app.route('/r/<int:request_id>')
def show(request_id):
	req = Request.query.get(request_id)
	return render_template("case.html", req = req)

@app.route('/request/<int:request_id>')
def show_request(request_id, template = None, record_uploaded = None, for_email_notification = False, banner_msg = None):
	current_user_id = None
	if current_user.is_anonymous() == False:
		current_user_id = current_user.id
	if not template:
		template = "case.html"
	req = get_resource("request", request_id)
	if not req:
		return render_template('error.html', message = "A request with ID %s does not exist." % request_id)
	if "Closed" in req['status']:
		template = "closed.html"
	return render_template(template, req = req, for_email_notification = for_email_notification, record_uploaded = record_uploaded, banner_msg = banner_msg, user_id = current_user_id)

@app.route('/add_a_<string:resource>', methods=['GET', 'POST'])
def add_a_resource(resource):
	if request.method == 'POST':
		add_resource(resource = resource, request_body = request, current_user_id = current_user.id)
		return show_request(request.form['request_id'], template = "manage_request_city.html")
	return render_template('error.html', message = "You can only add a %s from a request page!" %resource)

@app.route('/update_a_<string:resource>', methods=['GET', 'POST'])
def update_a_resource(resource):
	if request.method == 'POST':
		update_resource(resource, request)
		return show_request(request.form['request_id'], template = "case.html")
	return render_template('error.html', message = "You can only add a %s from a request page!" %resource)

# # Clears/updates tables in the database until I figure out how I want to deal with migrations
# @app.route('/clear')
# def clear_db():
# 	message = "You can't do that here."
# 	if app.config['ENVIRONMENT'] != "PRODUCTION":
# 		try:
# 			db.session.commit()
# 			db.drop_all()
# 			db.create_all()
# 			db.session.commit()
# 			return requests()
# 		except:
# 			message = "Dropping the tables didn't work :("
# 	return render_template('error.html', message = message)

# Closing is specific to a case, so this only gets called from a case (that only city staff have a view of)
@app.route('/close', methods=['POST'])
def close(request_id = None):
	if request.method == 'POST':
		template = 'closed.html'
		request_id = request.form['request_id']
		close_request(request_id, request.form['close_reason'])
		return show_request(request_id, template= template)
	return render_template('error.html', message = "You can only close from a requests page!")


# Shows all public records requests that have been made.
@app.route('/requests')
def requests():
	current_user_id = None
	if current_user.is_anonymous() == False:
		current_user_id = current_user.id
	all_record_requests = get_resources("request")
	if all_record_requests:
		return render_template('all_requests.html', all_record_requests = all_record_requests['objects'], user_id = current_user_id)
	else:
		return redirect(url_for(index()))

# Shows all public records requests that have been made by current owner. This doesn't work currently.
@app.route('/your_requests')
@login_required
def your_requests():
	all_record_requests = []
	owner_resource = get_resource_filter("owner", [dict(name='user_id', op='eq', val=current_user.id)])
	for owner in owner_resource['objects']:
		req_resource = get_resource_filter("request", [dict(name='current_owner', op='eq', val=owner['id'])])
		if req_resource['objects']:
			req = req_resource['objects'][0]
			all_record_requests.append(req)
	return render_template('all_requests.html', all_record_requests = all_record_requests, user_id = current_user.id)

# test template:  I clearly don't know what should go here, but need to keep a testbed here.
@app.route('/test')
def show_test():
	return render_template('test.html')

# # Admin page
# @app.route('/admin', methods=['GET', 'POST'])
# @login_required
# def admin():
# 	email = filters.user_name(current_user.id)
# 	if email != "an email":
# 		return index()
# 	if request.method == 'POST':
# 		# DO STUFF
# 	else:
# 		return render_template('admin.html')

@app.route('/<page>')
def any_page(page):
	try:
		return render_template('%s.html' %(page))
	except:
		return render_template('error.html', message = "%s totally doesn't exist." %(page))

@login_manager.user_loader
def load_user(userid):
	user = models.User.query.get(userid)
	return user

@app.route("/login", methods=["GET", "POST"])
def login(email=None):
	if request.method == 'POST':
		email = request.form['email']
	else:
		email = "richa@codeforamerica.org" # Obviously this is a hack for now
	if email_validation(email) == True:
		user = create_or_return_user(email=email)
		user_for_login = User.query.get(user['id'])
		login_user(user_for_login)
		return render_template('new_request.html', user_id = user['id'])
	else:
		return render_template('new_request.html', user_id = None) # TODO: Give feedback

@app.route("/logout")
@login_required
def logout():
	logout_user()
	return index()