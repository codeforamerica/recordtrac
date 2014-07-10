"""Contains all functions that render templates/html for the app.
"""

from flask import render_template, request, redirect, url_for, jsonify
from flask.ext.login import LoginManager, login_user, logout_user, current_user, login_required
from flaskext.browserid import BrowserID
from public_records_portal import app
from filters import *
from prr import add_resource, update_resource, make_request, close_request
from db_helpers import *
from db_helpers import get_user_by_id # finds a user by their id
from db_helpers import get_user # finds a user based on BrowserID response
import os, json
from urlparse import urlparse, urljoin
from notifications import send_prr_email, format_date
from spam import is_spam, is_working_akismet_key
from requests import get
from time import time
from flask.ext.cache import Cache
from recaptcha.client import captcha
from timeout import timeout
from flask import jsonify, request, Response
import anyjson
import helpers
import csv_export
from datetime import datetime, timedelta

# Initialize login

login_manager = LoginManager()
login_manager.user_loader(get_user_by_id)
login_manager.init_app(app)

browser_id = BrowserID()
browser_id.user_loader(get_user)
browser_id.init_app(app)

# Set flags:

check_for_spam = False
if app.config['ENVIRONMENT'] == 'PRODUCTION':
	check_for_spam = True

# Submitting a new request
def new_request(passed_recaptcha = False, data = None):
	user_id = get_user_id()
	if data or request.method == 'POST':
		if not data and not passed_recaptcha:
			data = request.form.copy()
		email = data['request_email']
		request_text = data['request_text']
		if request_text == "":
			return render_template('error.html', message = "You cannot submit an empty request.")
		if email == "" and 'ignore_email' not in data and not passed_recaptcha:
			return render_template('missing_email.html', form = data, user_id = get_user_id())
		if check_for_spam and is_spam(request_text) and not passed_recaptcha:
			return render_template('recaptcha.html', form = data, message = "Hmm, your request looks like spam. To submit your request, type the numbers or letters you see in the field below.", public_key = app.config['RECAPTCHA_PUBLIC_KEY'])

		alias = None
		phone = None
		offline_submission_type = None
		date_received = None
		if 'request_alias' in data:
			alias = data['request_alias']
		if 'request_phone' in data:
			phone = data['request_phone']
		if 'format_received' in data:
			offline_submission_type = data['format_received']
		if 'date_received' in data: # From the jQuery datepicker
			date_received = data['date_received']
			if date_received != "":
				try:
					date_received = datetime.strptime(date_received, '%m/%d/%Y') 
					date_received = date_received + timedelta(hours = 7) # This is somewhat of a hack, but we need to get this back in UTC (+7 hours offset from Pacific Time) time but still treat it as a 'naive' datetime object
				except ValueError:
					return render_template('error.html', message = "Please use the datepicker to select a date.")
		app.logger.info("\n\n Date received: %s" % date_received)
		request_id, is_new = make_request(text = request_text, email = email, user_id = user_id, alias = alias, phone = phone, passed_recaptcha = passed_recaptcha, department = data['request_department'], offline_submission_type = offline_submission_type, date_received = date_received)
		if is_new:
			return redirect(url_for('show_request_for_x', request_id = request_id, audience = 'new'))
		if not request_id:
			return render_template('error.html', message = "Your request looks a lot like spam.")
		app.logger.info("\n\nDuplicate request entered: %s" % request_text)
		return render_template('error.html', message = "Your request is the same as /request/%s" % request_id)
	else:
		routing_available = False
		if 'LIAISONS_FILEPATH' in app.config:
			routing_available = True
		if user_id:
			return render_template('offline_request.html', routing_available = routing_available, user_id = user_id)
		else:
			return render_template('new_request.html', routing_available = routing_available, user_id = user_id)

def to_csv():
	if get_user_id():
		return Response(csv_export.export(), mimetype='text/csv')
	else:
		return render_template('error.html', message = "You must be logged in to do this.")

def index():
	if current_user.is_anonymous() == False:
		return redirect(url_for('requests'))
	else:
		return landing()

def landing():
	viz_data_freq, viz_data_time = get_viz_data()
	return render_template('landing.html', viz_data_freq = json.dumps(viz_data_freq), viz_data_time = json.dumps(viz_data_time), user_id = get_user_id())

def viz():
	viz_data_freq, viz_data_time = get_viz_data()
	return render_template('viz.html', viz_data_freq = json.dumps(viz_data_freq), viz_data_time = json.dumps(viz_data_time))

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

def track(request_id = None):
	if request.method == 'POST':
		if not request_id:
			request_id = request.form['request_id']
		if not current_user.is_anonymous():
			audience = 'city'
		else:
			audience = 'public'
		return redirect(url_for('show_request_for_x', audience= audience, request_id = request_id))
	else:
		return render_template("track.html")

def unfollow(request_id, email):
	success = False
	user_id = create_or_return_user(email.lower())
	subscriber = get_subscriber(request_id = request_id, user_id = user_id)
	if subscriber:
		success = update_obj(attribute = "should_notify", val = False, obj = subscriber)
	if success:
		return show_request(request_id = request_id, template = "manage_request_unfollow.html")
	else:
		return render_template('error.html', message = "Unfollowing this request was unsuccessful. You probably weren't following it to begin with.")

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
	if req.status and "Closed" in req.status and template != "manage_request_feedback.html":
		template = "closed.html"
	return render_template(template, req = req, user_id = get_user_id())

def staff_to_json():
	users = User.query.filter(User.is_staff == True).all()
	staff_data = []
	for u in users:
		staff_data.append({'alias': u.alias, 'email': u.email})
	return jsonify(**{'objects': staff_data})

def departments_to_json():
	departments = Department.query.all()
	department_data = []
	for d in departments:
		department_data.append({'department': d.name})
	return jsonify(**{'objects': department_data})

def docs():
	return redirect('http://codeforamerica.github.io/public-records/docs/1.0.0')

@login_required
def edit_case(request_id):
	req = get_obj("Request", request_id)
	return render_template("edit_case.html", req = req, user_id = get_user_id())

@login_required
def add_a_resource(resource):
	if request.method == 'POST':
		resource_id = add_resource(resource = resource, request_body = request, current_user_id = current_user.id)
		if type(resource_id) == int or str(resource_id).isdigit():
			app.logger.info("\n\nSuccessfully added resource: %s with id: %s" % (resource, resource_id))
			return redirect(url_for('show_request_for_x', audience='city', request_id = request.form['request_id']))
		elif resource_id == False:
			app.logger.info("\n\nThere was an issue with adding resource: %s" % resource)
			return render_template('error.html')
		else:
			app.logger.info("\n\nThere was an issue with the upload: %s" % resource_id)
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
@timeout(seconds=25)
def requests():
	app.logger.debug("Processing requests.")
	try:
		departments = [d.name for d in Department.query.all()]
		user_id = get_user_id()
		total_requests_count = get_count("Request")
		template = 'all_requests.html'

		return render_template(template,
				   user_id = user_id,
				   title = "All Requests",
				   departments = departments,
				   total_requests_count = total_requests_count)
	except Exception, message:
		app.logger.info("\n\n%s" % message)
		if "Too long" in message:
			message = "Loading requests is taking a while. Try exploring with more restricted search options."
		else: 
			message = "Something went wrong loading the requests. We're looking into it!"
		return render_template('error.html', message = message, user_id = get_user_id())

def filter_department(department_name, results):
	app.logger.info("\n\nDepartment filter:%s." % department_name)
	if department_name and department_name != "All departments":
		department = Department.query.filter_by(name = department_name).first()
		if department:
			results = results.filter(Request.department_id == department.id)
		else:
			# Just return an empty query set
			results = results.filter(Request.department_id < 0)
	return results

def filter_search_term(search_input, results):
	if search_input:
		app.logger.info("Searching for '%s'." % search_input)
		search_terms = search_input.strip().split(" ") # Get rid of leading and trailing spaces and generate a list of the search terms
		num_terms = len(search_terms)
		# Set up the query
		search_query = ""
		if num_terms > 1:
			for x in range(num_terms - 1):
				search_query = search_query + search_terms[x] + ' & ' 
		search_query = search_query + search_terms[num_terms - 1] + ":*" # Catch substrings
		results = results.filter("to_tsvector(text) @@ to_tsquery('%s')" % search_query)
	return results

def fetch_requests():
	"""
	Ultra-custom API endpoint for serving up requests.
	Supports limit, search, and page parameters and returns json with an object that
	has a list of results in the 'objects' field.
	"""
	user_id = get_user_id()
	results = db.session.query(Request)

	# Filters!
	results = filter_department(department_name = request.args.get('department'), results = results)
	results = filter_search_term(search_input = request.args.get('search_term'), results = results)

	# Accumulate status filters
	status_filters = []

	if str(request.args.get('open')).lower() == 'true':
		status_filters.append(Request.open)

	if str(request.args.get('closed')).lower() == 'true':
		status_filters.append(Request.closed)

	date_format = '%m/%d/%Y'

	min_request_date = request.args.get('min_request_date')
	max_request_date = request.args.get('max_request_date')
	if min_request_date and max_request_date:
		min_request_date = datetime.strptime(min_request_date, date_format)
		max_request_date = datetime.strptime(max_request_date, date_format)
		results = results.filter(and_(Request.date_created >= min_request_date, Request.date_created <= max_request_date))
		app.logger.info('Request Date Bounding. Min: {0}, Max: {1}'.format(min_request_date, max_request_date))

	min_due_date = request.args.get('min_due_date')
	max_due_date = request.args.get('max_due_date')
	if min_due_date and max_due_date:
		min_due_date = datetime.strptime(min_due_date, date_format)
		max_due_date = datetime.strptime(max_due_date, date_format)
		results = results.filter(and_(Request.due_date >= min_due_date, Request.due_date <= max_due_date))
		app.logger.info('Due Date Bounding. Min: {0}, Max: {1}'.format(min_due_date, max_due_date))

	# Filters for agency staff only:
	if user_id:
		if str(request.args.get('due_soon')).lower() == 'true':
			status_filters.append(Request.due_soon)

		if str(request.args.get('overdue')).lower() == 'true':
			status_filters.append(Request.overdue)

		# Where am I the Point of Contact?
		if str(request.args.get('mine_as_poc')).lower() == 'true':
				results = results.filter(Request.id == Owner.request_id) \
								 .filter(Owner.user_id == user_id) \
								 .filter(Owner.is_point_person == True)

		# Where am I just a Helper?
		if str(request.args.get('mine_as_helper')).lower() == 'true':
				results = results.filter(Request.id == Owner.request_id) \
								 .filter(Owner.user_id == user_id) \
								 .filter(Owner.active == True)
		# Filter based on requester name
		requester_name = request.args.get('requester_name')
		if requester_name and requester_name != "":
			results = results.join(Subscriber, Request.subscribers).join(User).filter(func.lower(User.alias).like("%%%s%%" % requester_name.lower()))
			
	# Apply the set of status filters to the query.
	# Using 'or', they're non-exclusive!
	results = results.filter(or_(*status_filters))

	app.logger.info(status_filters)
	app.logger.info(str(results.statement.compile(dialect=postgresql.dialect())))

	sort_by = request.args.get('sort_column') 

	if sort_by and sort_by != '':
		ascending = request.args.get('sort_direction')
		app.logger.info("Sort Direction: %s" % ascending)
		app.logger.info("Sort Column: %s" % sort_by)
		if ascending == "asc":
			results = results.order_by((getattr(Request, sort_by)).asc())
		else:
			results = results.order_by((getattr(Request, sort_by)).desc())
	results = results.order_by(Request.id.desc())

	page_number = int(request.args.get('page_number') or 1)
	limit = int(request.args.get('limit') or 15)
	offset = limit * (page_number - 1)
	app.logger.info("Page Number: {0}, Limit: {1}, Offset: {2}".format(page_number, limit, offset))

	# Execute query
	more_results = False
	num_results = results.count()
	start_index = 0
	end_index = 0

	if num_results != 0:
		start_index = (page_number - 1) * limit
		if start_index == 0:
			start_index = 1
		if num_results > (limit * page_number):
			more_results = True
			end_index = start_index + 14
		else:
			end_index = num_results

	results = results.limit(limit).offset(offset).all()

	# TODO(cj@postcode.io): This map is pretty kludgy, we should be detecting columns and auto
	# magically making them fields in the JSON objects we return.
	results = map(lambda r: {     
		  "id":           r.id, \
		  "text":         helpers.clean_text(r.text), \
		  "date_created": helpers.date(r.date_received or r.date_created), \
		  "department":   r.department_name(), \
		  "requester":    r.requester_name(), \
		  "due_date":     format_date(r.due_date), \
		  "status":       r.status, \
		  # The following two attributes are defined as model methods,
		  # and not regular SQLAlchemy attributes.
		  "contact_name": r.point_person_name(), \
		  "solid_status": r.solid_status()
		   }, results)

	matches = {
		"objects": 		results,
		"num_results": 	num_results,
		"more_results": more_results,
		"start_index": 	start_index,
		"end_index": 	end_index
		}
	response = anyjson.serialize(matches)
	return Response(response, mimetype = "application/json")

def any_page(page):
	try:
		return render_template('%s.html' %(page), user_id = get_user_id())
	except:
		return render_template('error.html', message = "%s totally doesn't exist." %(page), user_id = get_user_id())

def tutorial():
	user_id = get_user_id()
	app.logger.info("\n\nTutorial accessed by user: %s." % user_id)
	return render_template('tutorial.html', user_id = user_id)

def login(email=None, password=None):
	if request.method == 'POST':
		email = request.form['email']
		password = request.form['password']
		user_to_login = authenticate_login(email, password)
		if user_to_login:
			login_user(user_to_login)
			redirect_url = get_redirect_target()
			if 'temporary_login' in redirect_url: # Redirect to update password
				return render_template('update_password.html', user_id = get_user_id())
			if 'login' in redirect_url or 'logout' in redirect_url:
				return redirect(url_for('index'))
			if "city" not in redirect_url:
					redirect_url = redirect_url.replace("/request/", "/city/request/")
			return redirect(redirect_url)
		else:
			app.logger.info("\n\nLogin failed (due to incorrect e-mail/password combo) for email: %s." % email)
			return render_template('error.html', message = "That e-mail/ password combo didn't work. You can always <a href='/reset_password'>reset your password</a>.")
		app.logger.info("\n\nLogin failed for email: %s." % email)
		return render_template('error.html', message="Something went wrong.", user_id = get_user_id())
	else:
		user_id = get_user_id()
		if user_id:
			return render_template('generic.html', message = 'You are already logged in. If you wish to log in as another user, first log out by clicking your name in the upper-right corner of this page and clicking Logout.', user_id = user_id)
		else:
			return render_template('generic.html', message = "If you work for the %s and are trying to log into RecordTrac, please log in by clicking City login in the upper-right corner of this page." % app.config['AGENCY_NAME'])

def reset_password(email=None):
	after_reset = False
	reset_success = False
	if request.method == 'POST':
		after_reset = True
		email = request.form['email']
		password = set_random_password(email)
		if password:
			send_prr_email(page = app.config['APPLICATION_URL'], recipients = [email], subject = "Your temporary password", template = "password_email.html", include_unsubscribe_link = False, password = password)
			reset_success = True
			app.logger.info("\n\nPassword reset sent for email: %s." % email)
		else:
			app.logger.info("\n\nPassword reset attempted and denied for email: %s." % email)
	return render_template('reset_password.html', after_reset = after_reset, reset_success = reset_success)


@login_required
def update_password(password=None):
	if request.method == 'POST':
		if set_password(current_user, request.form['password']):
			return index()
		app.logger.info("\n\nFailure updating password for user %s" % current_user.id)
		return render_template('error.html', message = "Something went wrong updating your password.")
	else:
		app.logger.info("\n\nSuccessfully updated password for user %s" % current_user.id)
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
	app.logger.info("Someone input %s" %(request_text))
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


def recaptcha():
	if request.method == 'POST':
		response = captcha.submit(
			request.form['recaptcha_challenge_field'],
			request.form['recaptcha_response_field'],
			app.config['RECAPTCHA_PRIVATE_KEY'],
			request.remote_addr
			)
		if not response.is_valid:
			message = "Invalid. Please try again."
			return render_template('recaptcha.html', message = message, public_key = app.config['RECAPTCHA_PUBLIC_KEY'], form = request.form)
		else:
			return new_request(passed_recaptcha = True, data = request.form)
	else:
		app.logger.info("\n\nAttempted access to recaptcha not via POST")
		return render_template('error.html', message = "You don't need to be here.")

def well_known_status():
	'''
	'''
	response = {
		'status': 'ok',
		'updated': int(time()),
		'dependencies': ['Akismet', 'Scribd', 'Sendgrid', 'Postgres'],
		'resources': {}
		}
	
	#
	# Try to connect to the database and get the first user.
	#
	try:
		if not get_obj('User', 1):
			raise Exception('Failed to get the first user')
		
	except Exception, e:
		response['status'] = 'Database fail: %s' % e
		return jsonify(response)
	
	#
	# Try to connect to Akismet and see if the key is valid.
	#
	try:
		if not is_working_akismet_key():
			raise Exception('Akismet reported a non-working key')
		
	except Exception, e:
		response['status'] = 'Akismet fail: %s' % e
		return jsonify(response)
	
	#
	# Try to ask Sendgrid how many emails we have sent in the past month.
	#
	try:
		url = 'https://sendgrid.com/api/stats.get.json?api_user=%(MAIL_USERNAME)s&api_key=%(MAIL_PASSWORD)s&days=30' % app.config
		got = get(url)
		
		if got.status_code != 200:
			raise Exception('HTTP status %s from Sendgrid /api/stats.get' % got.status_code)
		
		mails = sum([m['delivered'] + m['repeat_bounces'] for m in got.json()])
		response['resources']['Sendgrid'] = 100 * float(mails) / int(app.config.get('SENDGRID_MONTHLY_LIMIT') or 40000)
		
	except Exception, e:
		response['status'] = 'Sendgrid fail: %s' % e
		return jsonify(response)
	
	return jsonify(response)
