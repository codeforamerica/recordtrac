""" 
.. module:: db_helpers
	:synopsis: Functions that interact with the Postgres database via Flask-SQLAlchemy
.. modlueauthor:: Richa Agarwal <richa@codeforamerica.org>
"""


from public_records_portal import db, app
from models import *
from datetime import datetime, timedelta
from sqlalchemy.exc import IntegrityError, InvalidRequestError
from sqlalchemy import func, not_
import uuid
import json
import os

### @export "get_requester"
def get_requester(request_id): 
# Returns the first person who subscribed to a request, which is the requester
	subscribers = get_attribute(attribute = "subscribers", obj_id = request_id, obj_type = "Request")
	if subscribers:
		subscribers.sort(key = lambda x:x.date_created)
		return get_attribute(attribute = "user_id", obj = subscribers[0])
	return None


### @export "get_count"
def get_count(obj_type):
	return db.session.query(func.count(eval(obj_type).id)).scalar()

### @export "get_obj"
def get_obj(obj_type, obj_id):
	""" Query the database for an object via its class/type (defined in models.py) and ID and return the object. """
	if not obj_id:
		return None
	# There has to be a better way of doing this
	if obj_type == "User":
		return User.query.get(obj_id)
	elif obj_type == "Request":
		return Request.query.get(obj_id)
	elif obj_type == "Owner":
		return Owner.query.get(obj_id)
	elif obj_type == "Note":
		return Note.query.get(obj_id)
	elif obj_type == "QA":
		return QA.query.get(obj_id)
	elif obj_type == "Subscriber":
		return Subscriber.query.get(obj_id)
	elif obj_type == "Record":
		return Record.query.get(obj_id)
	return None

### @export "get_objs"
def get_objs(obj_type):
	""" Query the database for all objects of a certain class/type (defined in models.py) and return queryset. """
	# There has to be a better way of doing this
	if obj_type == "User":
		return User.query.all()
	elif obj_type == "Request":
		return Request.query.all()
	elif obj_type == "Owner":
		return Owner.query.all()
	elif obj_type == "Note":
		return Note.query.all()
	elif obj_type == "QA":
		return QA.query.all()
	elif obj_type == "Subscriber":
		return Subscriber.query.all()
	elif obj_type == "Record":
		return Record.query.all()
	return None

### @export "get_avg_response_time"
def get_avg_response_time(department):
	q = db.session.query(Request).join(Owner, Request.current_owner == Owner.id).join(User).filter(func.lower(User.department).like("%%%s%%" % department.lower())).all()
	response_time = None
	num_closed = 0
	for request in q:
		if request.status and 'Closed' in request.status:
			if response_time:
				response_time = response_time + (request.status_updated - request.date_created)
			else:
				response_time = request.status_updated - request.date_created
			num_closed = num_closed + 1
	if num_closed > 0:
		avg = response_time.seconds / num_closed
		return avg
	return None

### @export "get_request_by_owner"
def get_request_by_owner(owner_id):
	""" Return the request that a particular owner belongs to """
	if not owner_id:
		return None
	return Request.query.filter_by(current_owner = owner_id).first()

### @export "get_dept_by_request"
def get_dept_by_request(request):
	""" Return the department that a particular request belongs to """
	if not request.department: # If it wasn't specified at time of request, we guess using the current point of contact:
		try:
			point_of_contact = User.query.get(Owner.query.get(request.current_owner).user_id)
			return point_of_contact.department
		except:
			return None
	return request.department

### @export "get_owners_by_user_id"
def get_owners_by_user_id(user_id):
	""" Return the queryset of owners for a particular user. (A user can be associated with multiple owners)."""
	if not user_id:
		return None
	return Owner.query.filter_by(user_id = user_id)

### @export "get_owner_data"
def get_owner_data(request_id, attributes = ["alias"]):
	""" Return the alias of the current owner for a particular request. """
	owner_data = []
	if not request_id:
		return owner_data
	q = db.session.query(User).join(Owner, User.id == Owner.user_id).join(Request, Owner.id == Request.current_owner).filter(Request.id == request_id).all()
	for attribute in attributes:
		if len(q) > 0:
			owner_data.append(getattr(q[0], attribute))
		else:
			owner_data.append(None)
	return owner_data

### @export "get_prr_liaison_by_dept"
def get_contact_by_dept(dept):
	""" Return the contact for a given department. """
	q = db.session.query(User).filter(func.lower(User.contact_for).like("%%%s%%" % dept.lower()))
	return q[0].email

### @export "get_backup_by_dept"
def get_backup_by_dept(dept):
	""" Return the contact for a given department. """
	q = db.session.query(User).filter(func.lower(User.backup_for).like("%%%s%%" % dept.lower()))
	return q[0].email


### @export "get_requests_by_filters"
def get_requests_by_filters(filters_dict):
	""" Return the queryset of requests for the filters provided. """
	q = db.session.query(Request)
	if 'department' in filters_dict:
		q = q.join(Owner, Request.current_owner == Owner.id).join(User).filter(func.lower(User.department).like("%%%s%%" % filters_dict['department'].lower()))
		if 'owner' in filters_dict:
			q = q.filter(Request.id == Owner.request_id).filter(Owner.user_id == filters_dict['owner']) 
	else:
		if 'owner' in filters_dict:
			q = q.join(Owner, Request.id == Owner.request_id).filter(Owner.user_id == filters_dict['owner']) 
	for attr, value in filters_dict.items():
		if attr == 'department' or attr == 'owner':
			continue
		attr = attr.lower()
		if type(value) is str or type(value) is unicode:
			value = value.lower()
		if attr == 'status' and value == 'open':
			q = q.filter(not_(getattr(Request, 'status').like("%%%s%%" % 'Closed')))
		elif attr == 'requester': 
			q = q.join(Subscriber, Request.subscribers).join(User).filter(func.lower(User.alias).like("%%%s%%" % value))
		else:
			try:
				request_attr = getattr(Request, attr)
			except AttributeError:
				continue
			else:
				q = q.filter(request_attr).like("%%%s%%" % value)
	return q.all()

### @export "put_obj"
def put_obj(obj):
	""" Add and commit the object to the database. Return true if successful. """
	if obj:
		db.session.add(obj)
		db.session.commit()
		return True
	return False

### @export "get_attribute"
def get_attribute(attribute, obj_id = None, obj_type = None, obj = None):
	""" Obtain the object by obj_id and obj_type if obj is not provided, and return the specified attribute for that object. """
	if obj_id and obj_type:
		obj = get_obj(obj_type, obj_id)
	if obj:
		try:
			return getattr(obj, attribute)
		except:
			return None
	return None

### @export "update_obj"
def update_obj(attribute, val, obj_type = None, obj_id = None, obj = None):
	""" Obtain the object by obj_id and obj_type if obj is not provided, and update the specified attribute for that object. Return true if successful. """
	if obj_id and obj_type:
		obj = get_obj(obj_type, obj_id)
	if obj:
		try:
			setattr(obj, attribute, val)
			db.session.add(obj)
			db.session.commit()
			return True
		except:
			return False
	return False

### @export "create_QA"
def create_QA(request_id, question, owner_id):
	""" Create a QA object and return the ID. """
	qa = QA(request_id = request_id, question = question, owner_id = owner_id)
	db.session.add(qa)
	db.session.commit()
	return qa.id

### @export "create_request"
def create_request(text, user_id, department = None):
	""" Create a Request object and return the ID. """
	req = Request(text = text, creator_id = user_id, department = department)
	db.session.add(req)
	db.session.commit()
	return req.id

### @export "create_subscriber"
def create_subscriber(request_id, user_id):
	""" Create a Subscriber object and return the ID. """
	subscriber = Subscriber.query.filter_by(request_id = request_id, user_id = user_id).first()
	if not subscriber:
		subscriber = Subscriber(request_id = request_id, user_id = user_id)
		db.session.add(subscriber)
		db.session.commit()
		return subscriber.id, True
	return subscriber.id, False

### @export "create_note"
def create_note(request_id, text, user_id):
	""" Create a Note object and return the ID. """
	try:
		note = Note(request_id = request_id, text = text, user_id = user_id)
		put_obj(note)
		return note.id
	except:
		return None

### @export "create_record"
def create_record(request_id, user_id, description, doc_id = None, filename = None, access = None, url = None):
	# try:
		record = Record(doc_id = doc_id, request_id = request_id, user_id = user_id, description = description, filename = filename, url = url, access = access)
		put_obj(record)
		return record.id
	# except:
		# return None

def remove_obj(obj_type, obj_id):
	obj = get_obj(obj_type, obj_id)
	db.session.delete(obj)
	db.session.commit()

### @export "create_answer"
def create_answer(qa_id, subscriber_id, answer):
	qa = get_obj("QA", qa_id)
	qa.subscriber_id = subscriber_id
	qa.answer = answer
	db.session.add(qa)
	db.session.commit()
	return qa.request_id

### @export "create_or_return_user"
def create_or_return_user(email=None, alias = None, phone = None, department = None, not_id = False):
	if email:
		email = email.lower()
		user = User.query.filter_by(email = email).first()
		if not user:
			user = create_user(email = email, alias = alias, phone = phone, department = department)
		else:
			user = update_user(user, alias, phone, department)
		if not_id:
			return user
		return user.id
	else:
		user = create_user(alias = alias, phone = phone)
		return user.id

### @export "create_user"
def create_user(email=None, alias = None, phone = None, department = None):
	user = User(email = email, alias = alias, phone = phone, department = department, password = app.config['ADMIN_PASSWORD'])
	db.session.add(user)
	db.session.commit()
	return user

### @export "update_user"
def update_user(user, alias = None, phone = None, department = None):
	if alias:
		user.alias = alias
	if phone:
		user.phone = phone
	if department:
		user.department = department
	if not user.password:
		user.password = app.config['ADMIN_PASSWORD']
	db.session.add(user)
	db.session.commit()
	return user

### @export "create_owner"
def create_owner(request_id, reason, email = None, user_id = None):
	""" Adds a staff member to the request without assigning them as current owner. (i.e. "participant")
	Useful for multidepartmental requests."""
	if not user_id:
		user_id = create_or_return_user(email = email)
	participant = Owner(request_id = request_id, user_id = user_id, reason = reason)
	db.session.add(participant)
	db.session.commit()
	return participant.id

### @export "change_request_status"
def change_request_status(request_id, status):
	req = get_obj("Request", request_id)
	req.status = status
	req.status_updated = datetime.now().isoformat()
	db.session.add(req)
	db.session.commit()

### @export "find_request"
def find_request(text):
	req = Request.query.filter_by(text = text).first()
	if req:
		return req.id
	return None

### @export "find_owner"
def find_owner(request_id, user_id):
	owner = Owner.query.filter_by(request_id = request_id, user_id = user_id).first() 
	if owner:
		return owner.id
	return None

### @export "add_staff_participant"
def add_staff_participant(request_id, email = None, user_id = None, reason = None):
	""" Creates an owner for the request if it doesn't exist, and returns the owner ID and True if a new one was created. Returns the owner ID and False if existing."""
	if not user_id:
		user_id = create_or_return_user(email = email)
	participant = Owner.query.filter_by(request_id = request_id, user_id = user_id).first()
	if not participant:
		participant = Owner(request_id = request_id, user_id = user_id, reason = reason)
		db.session.add(participant)
		db.session.commit()
		return participant.id, True
	return participant.id, False

### @export "authenticate_login"
def authenticate_login(email, password):
	if email:
		user = create_or_return_user(email=email, not_id = True)
		if user.check_password(password):
			return user
		if user.password == password: # Hash it
			user.set_password(password)
			db.session.add(user)
			db.session.commit()
			return user
	return None

### @export "set_random_password"
def set_random_password(email):
	email = email.lower()
	user = User.query.filter_by(email = email).first()
	if not user or not user.department:
		return None # This is only for existing staff users, not a way to create a user, which we're not allowing yet.
	password = uuid.uuid4().hex
	user.set_password(password)
	db.session.add(user)
	db.session.commit()
	return password

### @export "set_password"
def set_password(user, password):
	try:
		user.set_password(password)
		db.session.add(user)
		db.session.commit()
		return True
	except:
		return False

### @export "update_subscriber"
def update_subscriber(request_id, alias, phone):
	""" Update a subscriber for a given request with the name and phone number provided. """
	user_id = create_or_return_user(alias = alias, phone = phone)
	r = Request.query.get(request_id)
	sub = r.subscribers[0]
	sub.user_id = user_id
	db.session.add(sub)
	db.session.commit()

### @export "get_viz_data"
def get_viz_data():
	viz_data = Visualization.query.get(1).content
	viz_time_data = Visualization.query.get(2).content
	viz_fastest_time_data = Visualization.query.get(3).content
	return json.loads(viz_data), json.loads(viz_fatest_time_data)

def create_viz_data():
	depts_freq = []
	depts_response_time = []
	depts_json = open(os.path.join(app.root_path, 'static/json/list_of_departments.json'))
	json_data = json.load(depts_json)
	for department in json_data:
		line = {}
		response_line = {}
		line['department'] = department
		response_line['department'] = department
		line['freq'] = len(get_requests_by_filters(line))
		avg_response_time = get_avg_response_time(department)
		if avg_response_time:
			response_line['time'] = avg_response_time
			depts_response_time.append(response_line)
		depts_freq.append(line)
	# Only display top 5 departments:
	depts_freq.sort(key = lambda x:x['freq'], reverse = True)
	depts_response_fastest_time = depts_response_time
	depts_response_time.sort(key = lambda x:x['time'], reverse = True)
	depts_response_fastest_time.sort(key = lambda x:x['time']) 
	del depts_freq[5:]
	del depts_response_time[5:]
	del depts_response_fastest_time[5:]
	viz = Visualization.query.get(1)
	viz2 = Visualization.query.get(2)
	viz3 = Visualization.query.get(3)
	if viz:
		viz.content = json.dumps(depts_freq)
	else:
		viz = Visualization(type_viz = 'freq', content = json.dumps(depts_freq))
	if viz2:
		viz2.content = json.dumps(depts_response_time)
		viz2.type_viz = 'time'
	else:
		viz = Visualization(type_viz = 'time', content = json.dumps(depts_response_time))
	if viz3:
		viz3.content = json.dumps(depts_response_fastest_time)
	db.session.add(viz)
	db.session.commit()
	
