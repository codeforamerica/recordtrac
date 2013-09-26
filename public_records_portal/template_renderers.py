"""Contains all functions that render templates/html for the app.
"""

from flask import render_template, request, redirect, url_for
from flask.ext.login import LoginManager, login_user, logout_user, current_user, login_required
from public_records_portal import app
from filters import *
from prr import add_resource, update_resource, make_request, close_request
from db_helpers import *
import departments
import os, json
from urlparse import urlparse, urljoin
from notifications import send_prr_email

# Initialize login
login_manager = LoginManager()
login_manager.init_app(app)

# Submitting a new request
def new_request():
	if request.method == 'POST':
		email = request.form['request_email']
		if email == "" and 'ignore_email' not in request.form:
			return render_template('missing_email.html', form = request.form, user_id = get_user_id())
		request_text = request.form['request_text']
		if request_text == "":
			return render_template('error.html', message = "You cannot submit an empty request.")
		alias = None
		phone = None
		if 'request_alias' in request.form:
			alias = request.form['request_alias']
		if 'request_phone' in request.form:
			phone = request.form['request_phone']
		assigned_to_email = app.config['DEFAULT_OWNER_EMAIL']
		assigned_to_reason = app.config['DEFAULT_OWNER_REASON']
		department = request.form['request_department']
		if department:
			prr_email = departments.get_prr_liaison(department)
			if prr_email:
				assigned_to_email = prr_email
				assigned_to_reason = "PRR Liaison for %s" %(department)
			else:
				print "%s is not a valid department" %(department)
		request_id, is_new = make_request(text = request_text, email = email, assigned_to_email = assigned_to_email, assigned_to_reason = assigned_to_reason, user_id = get_user_id(), alias = alias, phone = phone)
		if is_new:
			return redirect(url_for('show_request_for_x', request_id = request_id, audience = 'new'))
		if not request_id:
			return render_template('error.html', message = "You need to provide an e-mail address to submit a request.")
		return render_template('error.html', message = "Your request is the same as /request/%s" % request_id)
	else:
		return render_template('new_request.html', user_id = get_user_id())

def index():
	if current_user.is_anonymous() == False:
		return redirect(url_for('requests'))
	else:
		return redirect(url_for('new_request'))

# @login_required
# def your_requests():
# 	all_record_requests = []
# 	owners = get_owners_by_user_id(current_user.id)
# 	for owner in owners:
# 		req = get_request_by_owner(owner.id)
# 		if req:
# 			all_record_requests.append(req)
# 	return all_record_requests
	# return render_template('all_requests.html', all_record_requests = all_record_requests, user_id = current_user.id, title = "Requests assigned to you")

@app.errorhandler(404)
def page_not_found(e):
	return render_template('404.html'), 404

def explain_all_actions():
	action_json = open(os.path.join(app.root_path, 'static/json/actions.json'))
	json_data = json.load(action_json)
	actions = []
	for data in json_data:
		actions.append("%s: %s" %(data, json_data[data]["What"]))
	return render_template('actions.html', actions = actions)

# Returns a view of the case based on the audience. Currently views exist for city staff or general public.
def show_request_for_x(audience, request_id):
	if "city" in audience and current_user.is_anonymous():
		return render_template('alpha.html')
	return show_request(request_id = request_id, template = "manage_request_%s.html" %(audience))
show_request_for_x.methods = ['GET', 'POST']

def show_response(request_id):
	req = get_obj("Request", request_id)
	if not req:
		return render_template('error.html', message = "A request with ID %s does not exist." % request_id)
	return render_template("response.html", req = req, user_id = get_user_id())

def show_request(request_id, template = None):
	current_user_id = get_user_id()
	req = get_obj("Request", request_id)
	if not req:
		return render_template('error.html', message = "A request with ID %s does not exist." % request_id)
	if template:
		if "city" in template and not current_user_id:
			return render_template('alpha.html')
	else:
		template = "manage_request_public.html"
	if req.status and "Closed" in req.status:
		template = "closed.html"
	return render_template(template, req = req, user_id = get_user_id())


@login_required
def edit_case(request_id):
	req = get_obj("Request", request_id)
	return render_template("edit_case.html", req = req, user_id = get_user_id())

@login_required
def add_a_resource(resource):
	if request.method == 'POST':
		resource_id = add_resource(resource = resource, request_body = request, current_user_id = current_user.id)
		if type(resource_id) == int or str(resource_id).isdigit():
			return redirect(url_for('show_request_for_x', audience='city', request_id = request.form['request_id']))
		elif resource_id == False:
			return render_template('error.html')
		else:
			return render_template('help_with_uploads.html', message = resource_id)
	return render_template('error.html', message = "You can only update requests from a request page!")

def public_add_a_resource(resource):
	if request.method == 'POST':
		if 'note' in resource or 'subscriber' in resource: 
			resource_id = add_resource(resource = resource, request_body = request, current_user_id = None)
			if type(resource_id) == int:
				request_id = request.form['request_id']
				audience = 'public'
				if 'subscriber' in resource:
					audience = 'follower'
				return redirect(url_for('show_request_for_x', audience=audience, request_id = request_id))
	return render_template('error.html')

def update_a_resource(resource):
	if request.method == 'POST':
		update_resource(resource, request)
		if current_user.is_anonymous() == False:
			return redirect(url_for('show_request_for_x', audience='city', request_id = request.form['request_id']))
		else:
			return redirect(url_for('show_request', request_id = request.form['request_id']))
	return render_template('error.html', message = "You can only update requests from a request page!")

# Closing is specific to a case, so this only gets called from a case (that only city staff have a view of)
@login_required
def close(request_id = None):
	if request.method == 'POST':
		template = 'closed.html'
		request_id = request.form['request_id']
		close_request(request_id = request_id, reason = request.form['close_reason'], user_id = current_user.id)
		return show_request(request_id, template= template)
	return render_template('error.html', message = "You can only close from a requests page!")

# Shows all public records requests that have been made.
def requests():
	# Return first 100, ? limit = 100
	# Taken from list_of_departments.json:
	departments = sorted(["Human Resources", "Council District 7 - Larry Reid", "Department of Planning and Building", "Council District 5 - Noel Gallo", "Council District 3 - Lynette Gibson McElhaney", "City Clerk", "Council District 6 - Desley Brooks", "Health and Human Services", "Fire Department", "Budget and Revenue - Revenue Division", "Office of Controller and Treasury", "Information Technology (IT)", "City Attorney", "Council District 2 - Pat Kernighan", "Parks and Recreation", "City Auditor", "Council District 1 - Dan Kalb", "Office of the Mayor", "Council District 4 - Libby Schaaf", "Council At Large - Rebecca Kaplan", "Library Services", "Public Works Agency", "Contracts and Compliance", "City Administrator", "Office of Neighborhood Investment"], key=str.lower)
	filters = {}
	open_requests = False
	my_requests = False
	dept_selected = "All departments"
	if request.method == 'POST':
		if 'status_filter' in request.form:
			filters['status'] = 'open'
			open_requests = True
		if 'department_filter' in request.form and request.form['department_filter'] != '&nbsp':
			dept_selected = request.form['department_filter']
			if dept_selected != "All departments":
				filters['department'] = request.form['department_filter']
		if 'owner_requests' in request.form and current_user.is_anonymous() == False:
			my_requests = True
			filters['owner'] = current_user.id
	else:
		filters = request.args
	all_record_requests = get_requests_by_filters(filters)
	user_id = get_user_id()
	if all_record_requests:
		template = 'all_requests.html'
		if user_id: 
			template = 'all_requests_city.html'
		return render_template(template, all_record_requests = all_record_requests, user_id = user_id, title = "All Requests", open_requests = open_requests, departments = departments, dept_selected = dept_selected, my_requests = my_requests)
	else:
		return index()

@login_manager.unauthorized_handler
def unauthorized():
	return render_template('alpha.html')

@login_manager.user_loader
def load_user(userid):
	user = get_obj("User", userid)
	return user


# test template:  I clearly don't know what should go here, but need to keep a testbed here.
@app.route('/test')
def show_test():
	return render_template('test.html')

def any_page(page):
	try:
		return render_template('%s.html' %(page), user_id = get_user_id())
	except:
		return render_template('error.html', message = "%s totally doesn't exist." %(page), user_id = get_user_id())

def tutorial():
	return render_template('tutorial.html', user_id = get_user_id())

def login(email=None, password=None):
	if request.method == 'POST':
		email = request.form['email']
		password = request.form['password']
		user_to_login = authenticate_login(email, password)
		if user_to_login:
			login_user(user_to_login)
			redirect_url = get_redirect_target()
			if 'login' in redirect_url:
				return redirect(url_for('index'))
			else:
				return redirect(get_redirect_target())
	return render_template('error.html', message = "Your e-mail/ password combo didn't work. You can always <a href='/reset_password'>reset your password</a>.")

def reset_password(email=None):
	if request.method == 'POST':
		email = request.form['email']
		password = set_random_password(email)
		if password:
			send_prr_email(page = app.config['APPLICATION_URL'], recipients = [email], subject = "Your temporary password", template = "password_email.html", include_unsubscribe_link = False, password = password)
			message = "Thanks! You should receive an e-mail shortly with instructions on how to login and update your password."
		else:
			message = "Looks like you're not a user already. Currently, this system requires logins only for city employees. "
	return render_template('reset_password.html', message = message)


@login_required
def update_password(password=None):
	if request.method == 'POST':
		if set_password(current_user, request.form['password']):
			return index()
		return render_template('error.html', message = "Something went wrong updating your password.")
	else:
		return render_template('update_password.html', user_id = current_user.id)

def staff_card(user_id):
	return render_template('staff_card.html', uid = user_id)

def logout():
	logout_user()
	return index()

def get_user_id():
	if current_user.is_anonymous() == False:
		return current_user.id
	return None

# Used as AJAX POST endpoint to check if new request text contains certain keyword
# See new_requests.(html/js)
def is_public_record():
	request_text = request.form['request_text']

	not_records_filepath = os.path.join(app.root_path, 'static/json/notcityrecords.json')
	not_records_json = open(not_records_filepath)
	json_data = json.load(not_records_json)
	request_text = request_text.lower()
	if "birth" in request_text or "death" in request_text or "marriage" in request_text:
		return json_data["Certificate"]
	if "divorce" in request_text:
		return json_data["Divorce"]
	return ''

def get_redirect_target():
	""" Taken from http://flask.pocoo.org/snippets/62/ """
	for target in request.values.get('next'), request.referrer:
		if not target:
			continue
		if is_safe_url(target):
			return target

def is_safe_url(target):
	""" Taken from http://flask.pocoo.org/snippets/62/ """
	ref_url = urlparse(request.host_url)
	test_url = urlparse(urljoin(request.host_url, target))
	return test_url.scheme in ('http', 'https') and \
		ref_url.netloc == test_url.netloc
