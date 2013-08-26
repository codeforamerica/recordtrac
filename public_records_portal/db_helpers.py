from public_records_portal import db
from models import User, Request, Owner, Note, QA, Subscriber
from datetime import datetime, timedelta
from sqlalchemy.exc import IntegrityError, InvalidRequestError
from sqlalchemy import func

def get_obj(obj_type, obj_id):
	# There has to be a better way of doing this
	print "Object Type, ID: %s %s" % (obj_type, obj_id)
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
	return None

def get_objs(obj_type):
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
	return None

def get_request_by_owner(owner_id):
	return Request.query.filter_by(current_owner = owner_id).first()

def get_owners_by_user_id(user_id):
	return Owner.query.filter_by(user_id = user_id)

def put_obj(obj):
	db.session.add(obj)
	db.session.commit()

def get_attribute(attribute, obj_id = None, obj_type = None, obj = None):
	if obj_id and obj_type:
		obj = get_obj(obj_type, obj_id)
	if obj:
		try:
			return getattr(obj, attribute)
		except:
			return None
	return None


def update_obj(attribute, val, obj_type = None, obj_id = None, obj = None):
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

def create_note(request_id, text, user_id):
	try:
		note = Note(request_id = request_id, text = text, user_id = user_id)
		put_obj(note)
		return note.id
	except:
		return None

def create_record(doc_id, request_id, user_id, description, filename, url):
	try:
		record = Record(doc_id = doc_id, request_id = request_id, user_id = user_id, descrption = description, filename = filename, url = url)
		put_obj(record)
		return record.id
	except:
		return None

def remove_obj(obj_type, obj_id):
	obj = get_obj(obj_type, obj_id)
	db.session.delete(obj)
	db.session.commit()

def create_or_return_user(email, alias = None, phone = None, department = None):
	user = User.query.filter(func.lower(User.email) == func.lower(email)).first() 
	if not user:
		user = User(email = email, alias = alias, phone = phone, department = department, password = app.config['ADMIN_PASSWORD'])
	else:
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

def create_owner(request_id, reason, email):
	""" Adds a staff member to the request without assigning them as current owner. (i.e. "participant")
	Useful for multidepartmental requests."""
	user = create_or_return_user(email = email)
	participant = Owner(request_id = request_id, user_id = user.id, reason = reason)
	db.session.add(participant)
	db.session.commit()
	return participant.id

def change_request_status(request_id, status):
	req = get_obj("Request", request_id)
	req.status = status
	req.status_updated = datetime.now().isoformat()
	db.session.add(req)
	db.session.commit()


