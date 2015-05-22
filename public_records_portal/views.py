"""
    public_records_portal.views
    ~~~~~~~~~~~~~~~~

    Implements functions that render the Jinja (http://jinja.pocoo.org/) templates/html for RecordTrac.

"""


from flask import render_template, request, redirect, url_for, jsonify
from flask.ext.login import LoginManager, login_user, logout_user, current_user, login_required
from flaskext.browserid import BrowserID
from public_records_portal import app, db, models
from prr import add_resource, update_resource, make_request, close_request
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
from filters import *
import re
from db_helpers import get_count, get_obj
from sqlalchemy import func, not_, and_, or_
import pytz

# Initialize login

login_manager = LoginManager()
login_manager.user_loader(get_user_by_id)
login_manager.init_app(app)

browser_id = BrowserID()
browser_id.user_loader(get_user)
browser_id.init_app(app)


# Submitting a new request
@app.route("/new", methods=["GET", "POST"])
def new_request(passed_recaptcha = False, data = None):
	if data or request.method == 'POST':
		if not data and not passed_recaptcha:
			data = request.form.copy()
		email = data['request_email']
		request_text = data['request_text']
		if request_text == "":
			return render_template('error.html', message = "You cannot submit an empty request.")
		if email == "" and 'ignore_email' not in data and not passed_recaptcha:
			return render_template('missing_email.html', form = data)
		if not passed_recaptcha and (is_spam(comment = request_text, user_ip = request.remote_addr, user_agent = request.headers.get('User-Agent'))):
			return render_template('recaptcha_request.html', form = data, message = "Hmm, your request looks like spam. To submit your request, type the numbers or letters you see in the field below.")

		alias = None
		phone = None
		offline_submission_type = None
		date_received = None
		department = None
		if 'request_department' in data:
			department = data['request_department']
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
					tz = pytz.timezone(app.config['TIMEZONE'])
					offset = tz.utcoffset(datetime.now())
					offset = (offset.days * 86400 + offset.seconds) / 3600
					date_received = date_received - timedelta(hours = offset) # This is somewhat of a hack, but we need to get this back in UTC time but still treat it as a 'naive' datetime object
				except ValueError:
					return render_template('error.html', message = "Please use the datepicker to select a date.")
		request_id, is_new = make_request(text = request_text, email = email, alias = alias, phone = phone, passed_spam_filter = True, department = department, offline_submission_type = offline_submission_type, date_received = date_received)
		if is_new:
			return redirect(url_for('show_request_for_x', request_id = request_id, audience = 'new'))
		if not request_id:
			return render_template('error.html', message = "Your request looks a lot like spam.")
		app.logger.info("\n\nDuplicate request entered: %s" % request_text)
		return render_template('error.html', message = "Your request is the same as /request/%s" % request_id)
	else:
		departments = None
		routing_available = False
		if 'LIAISONS_URL' in app.config:
			routing_available = True
			departments = db.session.query(models.Department).all()
		if current_user.is_authenticated():
			return render_template('offline_request.html', routing_available = routing_available, departments = departments)
		else:
			return render_template('new_request.html', routing_available = routing_available, departments = departments)

@app.route("/export")
@login_required
def to_csv():
	return Response(csv_export.export(), mimetype='text/csv')

@app.route("/", methods = ["GET", "POST"])
def index():
	if current_user.is_anonymous() == False:
		return redirect(url_for('display_all_requests'))
	else:
		return landing()

@app.route("/landing")
def landing():
	return render_template('landing.html')

@login_manager.unauthorized_handler
def unauthorized():
    return render_template("alpha.html")

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
@app.route("/<string:audience>/request/<int:request_id>")
def show_request_for_x(audience, request_id):
	if "city" in audience:
		return show_request_for_city(request_id = request_id)
	return show_request(request_id = request_id, template = "manage_request_%s.html" %(audience))
show_request_for_x.methods = ['GET', 'POST']


@app.route("/city/request/<int:request_id>")
@login_required
def show_request_for_city(request_id):
	if is_supported_browser():
		return show_request(request_id = request_id, template = "manage_request_city.html")
	else:
		return show_request(request_id = request_id, template = "manage_request_city_less_js.html")

@app.route("/response/<int:request_id>")
def show_response(request_id):
	req = get_obj("Request", request_id)
	if not req:
		return render_template('error.html', message = "A request with ID %s does not exist." % request_id)
	return render_template("response.html", req = req)

@app.route("/track", methods = ["POST"])
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

@app.route("/unfollow/<int:request_id>/<string:email>")
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

@app.route("/request/<int:request_id>")
def show_request(request_id, template = "manage_request_public.html"):
	req = get_obj("Request", request_id)
	if not req:
		return render_template('error.html', message = "A request with ID %s does not exist." % request_id)
	if req.status and "Closed" in req.status and template != "manage_request_feedback.html":
		template = "closed.html"
	return render_template(template, req = req)

@app.route("/api/staff")
def staff_to_json():
	users = models.User.query.filter(models.User.is_staff == True).all()
	staff_data = []
	for u in users:
		staff_data.append({'alias': u.alias, 'email': u.email})
	return jsonify(**{'objects': staff_data})

@app.route("/api/departments")
def departments_to_json():
	departments = models.Department.query.all()
	department_data = []
	for d in departments:
		department_data.append({'department': d.name})
	return jsonify(**{'objects': department_data})

def docs():
	return redirect('http://codeforamerica.github.io/public-records/docs/1.0.0')

@app.route("/edit/request/<int:request_id>")
@login_required
def edit_case(request_id):
	req = get_obj("Request", request_id)
	return render_template("edit_case.html", req = req)

@app.route("/add_a_<string:resource>", methods = ["GET", "POST"])
@login_required
def add_a_resource(resource):
	if request.method == 'POST':
		resource_id = add_resource(resource = resource, request_body = request.form, current_user_id = get_user_id())
		if type(resource_id) == int or str(resource_id).isdigit():
			app.logger.info("\n\nSuccessfully added resource: %s with id: %s" % (resource, resource_id))
			return redirect(url_for('show_request_for_city', request_id = request.form['request_id']))
		elif resource_id == False:
			app.logger.info("\n\nThere was an issue with adding resource: %s" % resource)
			return render_template('error.html')
		else:
			app.logger.info("\n\nThere was an issue with the upload: %s" % resource_id)
			return render_template('help_with_uploads.html', message = resource_id)
	return render_template('error.html', message = "You can only update requests from a request page!")

@app.route("/public_add_a_<string:resource>", methods = ["GET", "POST"])
def public_add_a_resource(resource, passed_recaptcha = False, data = None):
	if (data or request.method == 'POST') and ('note' in resource or 'subscriber' in resource):
			if not data:
					data = request.form.copy()
			if 'note' in resource:
				if not passed_recaptcha and is_spam(comment = data['note_text'], user_ip = request.remote_addr, user_agent = request.headers.get('User-Agent')):
					return render_template('recaptcha_note.html', form = data, message = "Hmm, your note looks like spam. To submit your note, type the numbers or letters you see in the field below.")
				resource_id = prr.add_note(request_id = data['request_id'], text = data['note_text'], passed_spam_filter = True)
			else:
				resource_id = prr.add_resource(resource = resource, request_body = data, current_user_id = None)
			if type(resource_id) == int:
				request_id = data['request_id']
				audience = 'public'
				if 'subscriber' in resource:
					audience = 'follower'
				return redirect(url_for('show_request_for_x', audience=audience, request_id = request_id))
	return render_template('error.html')

@app.route("/update_a_<string:resource>", methods = ["GET", "POST"])
def update_a_resource(resource, passed_recaptcha = False, data = None):
	if (data or request.method == 'POST'):
		if not data:
			data = request.form.copy()
		if 'qa' in resource:
			if not passed_recaptcha and is_spam(comment = data['answer_text'], user_ip = request.remote_addr, user_agent = request.headers.get('User-Agent')):
				return render_template('recaptcha_answer.html', form = data, message = "Hmm, your answer looks like spam. To submit your answer, type the numbers or letters you see in the fiel dbelow.")
			prr.answer_a_question(qa_id = int(data['qa_id']), answer = data['answer_text'], passed_spam_filter = True)
		else:
			update_resource(resource, data)			
		if current_user.is_anonymous() == False:
			return redirect(url_for('show_request_for_city', request_id = request.form['request_id']))
		else:
			return redirect(url_for('show_request', request_id = request.form['request_id']))
	return render_template('error.html', message = "You can only update requests from a request page!")

# Closing is specific to a case, so this only gets called from a case (that only city staff have a view of)
@app.route("/close", methods = ["GET", "POST"])
@login_required
def close(request_id = None):
	if request.method == 'POST':
		template = 'closed.html'
		request_id = request.form['request_id']
		reason = ""
		if 'close_reason' in request.form:
			reason = request.form['close_reason']
		elif 'close_reasons' in request.form:
			for close_reason in request.form.getlist('close_reasons'):
				reason += close_reason + " "
		close_request(request_id = request_id, reason = reason, user_id = get_user_id())
		return show_request(request_id, template= template)
	return render_template('error.html', message = "You can only close from a requests page!")


def filter_department(departments_selected, results):
	if departments_selected and 'All departments' not in departments_selected:
		app.logger.info("\n\nDepartment filters:%s." % departments_selected)
		department_ids = []
		for department_name in departments_selected:
			if department_name:
				department = models.Department.query.filter_by(name = department_name).first()
				if department:
					department_ids.append(department.id)
		if department_ids:
			results = results.filter(models.Request.department_id.in_(department_ids))
		else:
			# Just return an empty query set
			results = results.filter(models.Request.department_id < 0)
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

def get_filter_value(filters_map, filter_name, is_list = False, is_boolean = False):
	if filter_name in filters_map:
		val = filters_map[filter_name]
		if filter_name == 'department' and val:
			return [val]
		elif is_list:
			return filters_map.getlist(filter_name)
		elif is_boolean:
			return str(val.lower())
		else:
			return val
	return None

def is_supported_browser():
	browser = request.user_agent.browser
	version = request.user_agent.version and int(request.user_agent.version.split('.')[0])
	platform = request.user_agent.platform
	uas = request.user_agent.string
	if browser and version:
		if (browser == 'msie' and version < 9) \
		or (browser == 'firefox' and version < 4) \
		or (platform == 'android' and browser == 'safari' and version < 534) \
		or (platform == 'iphone' and browser == 'safari' and version < 7000) \
		or ((platform == 'macos' or platform == 'windows') and browser == 'safari' and not re.search('Mobile', uas) and version < 534) \
		or (re.search('iPad', uas) and browser == 'safari' and version < 7000) \
		or (platform == 'windows' and re.search('Windows Phone OS', uas)) \
		or (browser == 'opera') \
		or (re.search('BlackBerry', uas)):
			return False
	return True

@app.route("/view_requests")
def display_all_requests(methods = ["GET"]):
	""" Dynamically load requests page depending on browser. """ 
	if is_supported_browser():
		return backbone_requests()
	else:
		return no_backbone_requests()

@app.route("/view_requests_backbone")
def backbone_requests():
	return render_template("all_requests.html", departments = db.session.query(models.Department).all(), total_requests_count = get_count("Request"))

@app.route("/view_requests_no_backbone")
def no_backbone_requests():
	return fetch_requests()

@app.route("/requests", methods = ["GET"])
def fetch_requests(output_results_only = False, filters_map = None, date_format = '%Y-%m-%d', checkbox_value = 'on'):

	user_id = get_user_id()

	if not filters_map:
		if request.args: 
			if is_supported_browser():
				return backbone_requests()
			else: # Clear URL
				filters_map = request.args
		else:
			filters_map = request.form

	# Set defaults 
	is_open = checkbox_value
	is_closed = None
	due_soon = checkbox_value
	overdue = checkbox_value
	mine_as_poc = checkbox_value
	mine_as_helper = checkbox_value
	departments_selected = []
	sort_column = "id"
	sort_direction = "asc"
	min_due_date = None
	max_due_date = None
	min_date_received = None
	max_date_received = None
	requester_name = None 
	page_number = 1
	search_term = None

	if filters_map:
		departments_selected = get_filter_value(filters_map = filters_map, filter_name = 'departments_selected', is_list = True) or get_filter_value(filters_map, 'department')
		is_open = get_filter_value(filters_map = filters_map, filter_name = 'is_open', is_boolean = True)
		is_closed = get_filter_value(filters_map = filters_map, filter_name = 'is_closed', is_boolean = True)
		due_soon = get_filter_value(filters_map = filters_map, filter_name = 'due_soon', is_boolean = True)
		overdue = get_filter_value(filters_map = filters_map, filter_name = 'overdue', is_boolean = True)
		mine_as_poc = get_filter_value(filters_map = filters_map, filter_name = 'mine_as_poc', is_boolean = True)
		mine_as_helper = get_filter_value(filters_map = filters_map, filter_name = 'mine_as_helper', is_boolean = True)
		sort_column = get_filter_value(filters_map, 'sort_column') or 'id'
		sort_direction = get_filter_value(filters_map, 'sort_direction') or 'asc'
		search_term = get_filter_value(filters_map, 'search_term')
		min_due_date = get_filter_value(filters_map, 'min_due_date')
		max_due_date = get_filter_value(filters_map, 'max_due_date')
		min_date_received = get_filter_value(filters_map, 'min_date_received')
		max_date_received = get_filter_value(filters_map, 'max_date_received')
		requester_name = get_filter_value(filters_map, 'requester_name')
		page_number = int(get_filter_value(filters_map, 'page_number') or '1')


	results = get_results_by_filters(departments_selected = departments_selected, is_open = is_open, is_closed = is_closed, due_soon = due_soon, overdue = overdue, mine_as_poc = mine_as_poc, mine_as_helper = mine_as_helper, sort_column = sort_column, sort_direction = sort_direction, search_term = search_term, min_due_date = min_due_date, max_due_date = max_due_date, min_date_received = min_date_received, max_date_received = max_date_received, requester_name = requester_name, page_number = page_number, user_id = user_id, date_format = date_format, checkbox_value = checkbox_value)

	# Execute query
	limit = 15
	offset = limit * (page_number - 1)
	app.logger.info("Page Number: {0}, Limit: {1}, Offset: {2}".format(page_number, limit, offset))
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
	requests = prepare_request_fields(results = results)
	if output_results_only == True:
		return requests, num_results, more_results, start_index, end_index

	return render_template("all_requests_less_js.html", total_requests_count = get_count("Request"), requests = requests, departments = db.session.query(models.Department).all(), departments_selected = departments_selected, is_open = is_open, is_closed = is_closed, due_soon = due_soon, overdue = overdue, mine_as_poc = mine_as_poc, mine_as_helper = mine_as_helper, sort_column = sort_column, sort_direction = sort_direction, search_term = search_term, min_due_date = min_due_date, max_due_date = max_due_date, min_date_received = min_date_received, max_date_received = max_date_received, requester_name = requester_name, page_number = page_number, more_results = more_results, num_results = num_results, start_index = start_index, end_index = end_index)

@app.route("/custom/request", methods = ["GET", "POST"])
def json_requests():
	"""
	Ultra-custom API endpoint for serving up requests.
	Supports limit, search, and page parameters and returns json with an object that
	has a list of results in the 'objects' field.
	"""
	objects, num_results, more_results, start_index, end_index = fetch_requests(output_results_only = True, filters_map = request.args, date_format = '%m/%d/%Y', checkbox_value = 'true')
	matches = {
		"objects": 		objects,
		"num_results": 	num_results,
		"more_results": more_results,
		"start_index": 	start_index,
		"end_index": 	end_index
		}
	response = anyjson.serialize(matches)
	return Response(response, mimetype = "application/json")

def prepare_request_fields(results):
	if current_user.is_anonymous():
		return map(lambda r: {     
			  "id":           r.id, \
			  "text":         helpers.clean_text(r.text), \
			  "date_received": helpers.date(r.date_received or r.date_created), \
			  "department":   r.department_name(), \
			  "status":       r.status, \
			  # The following two attributes are defined as model methods,
			  # and not regular SQLAlchemy attributes.
			  "contact_name": r.point_person_name(), \
			  "solid_status": r.solid_status()
			   }, results)
	else:
		return map(lambda r: {     
			  "id":           r.id, \
			  "text":         helpers.clean_text(r.text), \
			  "date_received": helpers.date(r.date_received or r.date_created), \
			  "department":   r.department_name(), \
			  "requester":    r.requester_name(), \
			  "due_date":     format_date(r.due_date), \
			  "status":       r.status, \
			  # The following two attributes are defined as model methods,
			  # and not regular SQLAlchemy attributes.
			  "contact_name": r.point_person_name(), \
			  "solid_status": r.solid_status()
			   }, results)


def get_results_by_filters(departments_selected, is_open, is_closed, due_soon, overdue, mine_as_poc, mine_as_helper, sort_column, sort_direction, search_term, min_due_date, max_due_date, min_date_received, max_date_received, requester_name, page_number, user_id, date_format, checkbox_value):
	# Initialize query
	results = db.session.query(models.Request)

	# Set filters on the query

	results = filter_department(departments_selected = departments_selected, results = results)
	results = filter_search_term(search_input = search_term, results = results)

	# Accumulate status filters
	status_filters = []

	if is_open == checkbox_value:
		status_filters.append(models.Request.open)
		if not user_id:
			status_filters.append(models.Request.due_soon)
			status_filters.append(models.Request.overdue)

	if is_closed == checkbox_value:
		status_filters.append(models.Request.closed)

	if min_date_received and max_date_received and min_date_received != "" and max_date_received != "":
		try:
			min_date_received = datetime.strptime(min_date_received, date_format)
			max_date_received = datetime.strptime(max_date_received, date_format) + timedelta(hours = 23, minutes = 59) 
			results = results.filter(and_(models.Request.date_received >= min_date_received, models.Request.date_received <= max_date_received))
			app.logger.info('Request Date Bounding. Min: {0}, Max: {1}'.format(min_date_received, max_date_received))
		except:
			app.logger.info('There was an error parsing the request date filters. Received Min: {0}, Max {1}'.format(min_date_received, max_date_received))


	# Filters for agency staff only:
	if user_id:

		if due_soon == checkbox_value:
			status_filters.append(models.Request.due_soon)

		if overdue == checkbox_value:
			status_filters.append(models.Request.overdue)

		if min_due_date and max_due_date and min_due_date != "" and max_due_date != "":
			try:
				min_due_date = datetime.strptime(min_due_date, date_format)
				max_due_date = datetime.strptime(max_due_date, date_format) + timedelta(hours = 23, minutes = 59)  
				results = results.filter(and_(models.Request.due_date >= min_due_date, models.Request.due_date <= max_due_date))
				app.logger.info('Due Date Bounding. Min: {0}, Max: {1}'.format(min_due_date, max_due_date))
			except:
				app.logger.info('There was an error parsing the due date filters. Due Date Min: {0}, Max {1}'.format(min_due_date, max_due_date))

		# PoC and Helper filters
		if mine_as_poc == checkbox_value: 
			if mine_as_helper == checkbox_value:
				# Where am I the Point of Contact *or* the Helper?
				results = results.filter(models.Request.id == models.Owner.request_id) \
								 .filter(models.Owner.user_id == user_id) \
								 .filter(models.Owner.active == True)
			else:
				# Where am I the Point of Contact only?
				results = results.filter(models.Request.id == models.Owner.request_id) \
								 .filter(models.Owner.user_id == user_id) \
								 .filter(models.Owner.is_point_person == True)
		elif mine_as_helper == checkbox_value:
				# Where am I a Helper only?
				results = results.filter(models.Request.id == Owner.request_id) \
								 .filter(models.Owner.user_id == user_id) \
								 .filter(models.Owner.active == True) \
								 .filter(models.Owner.is_point_person == False)
		# Filter based on requester name
		requester_name = requester_name
		if requester_name and requester_name != "":
			results = results.join(models.Subscriber, models.Request.subscribers).join(models.User).filter(func.lower(models.User.alias).like("%%%s%%" % requester_name.lower()))
			
	# Apply the set of status filters to the query.
	# Using 'or', they're non-exclusive!
	results = results.filter(or_(*status_filters))

	if sort_column:
		app.logger.info("Sort Direction: %s" % sort_direction)
		app.logger.info("Sort Column: %s" % sort_column)
		if sort_direction == "desc":
			results = results.order_by((getattr(models.Request, sort_column)).desc())
		else:
			results = results.order_by((getattr(models.Request, sort_column)).asc())

	return results.order_by(models.Request.id.desc())


@app.route("/<page>")
def any_page(page):
	try:
		return render_template('%s.html' %(page))
	except:
		return render_template('error.html', message = "%s totally doesn't exist." %(page))

def tutorial():
	user_id = get_user_id()
	app.logger.info("\n\nTutorial accessed by user: %s." % user_id)
	return render_template('tutorial.html')

@app.route("/staff_card/<int:user_id>")
def staff_card(user_id):
	return render_template('staff_card.html', uid = user_id)

@app.route("/logout")
@login_required
def logout():
	logout_user()
	return index()

def get_user_id():
	if current_user.is_authenticated():
		return current_user.id
	return None

# Used as AJAX POST endpoint to check if new request text contains certain keyword
# See new_requests.(html/js)
@app.route("/is_public_record", methods = ["POST"])
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


@app.route("/recaptcha_<string:templatetype>", methods = ["GET", "POST"])
def recaptcha_templatetype(templatetype):
	if request.method == 'POST':
		template = "recaptcha_" + templatetype + ".html"
		response = captcha.submit(
			request.form['recaptcha_challenge_field'],
			request.form['recaptcha_response_field'],
			app.config['RECAPTCHA_PRIVATE_KEY'],
			request.remote_addr
			)
		if not response.is_valid:
			message = "Invalid. Please try again."
			return render_template(template, message = message, form = request.form)
		else:
			if templatetype == "note":
				return public_add_a_resource(passed_recaptcha = True, data = request.form, resource = "note")
			elif templatetype == "answer":
				app.logger.info("Template type is answer!")
				return update_a_resource(passed_recaptcha = True, data = request.form, resource = "qa")
			elif templatetype == "request":
				return new_request(passed_recaptcha = True, data = request.form)
	else:
		app.logger.info("\n\nAttempted access to recaptcha not via POST")
		return render_template('error.html', message = "You don't need to be here.")

@app.route("/.well-known/status", methods = ["GET"])
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
