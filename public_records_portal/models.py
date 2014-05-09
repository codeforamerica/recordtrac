from flask.ext.sqlalchemy import SQLAlchemy, sqlalchemy
from flask.ext.login import current_user

from sqlalchemy import Table, Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method

from datetime import datetime, timedelta
from public_records_portal import db, app
from werkzeug.security import generate_password_hash, check_password_hash
import json
import re


### @export "User"
class User(db.Model):
	__tablename__ = 'user'
	id = db.Column(db.Integer, primary_key = True)
	alias = db.Column(db.String(100))
	email = db.Column(db.String(100), unique=True)
	phone = db.Column(db.String())
	date_created = db.Column(db.DateTime)
	password = db.Column(db.String(255))
	department = db.Column(Integer, ForeignKey("department.id"))
	current_department = relationship("Department", foreign_keys = [department], uselist = False)
	contact_for = db.Column(db.String()) # comma separated list
	backup_for = db.Column(db.String()) # comma separated list
	owners = relationship("Owner")
	subscribers = relationship("Subscriber")

	def is_authenticated(self):
		return True
	def is_active(self):
		return True
	def is_anonymous(self):
		return False
	def get_id(self):
		return unicode(self.id)
	def set_password(self, password):
		self.password = generate_password_hash(password)
	def check_password(self, password):
		return check_password_hash(self.password, password)
	def get_alias(self):
		if self.alias and self.alias != "":
			return self.alias
		return "N/A"
	def __init__(self, email=None, alias = None, phone=None, department = None, password=None):
		self.email = email
		self.alias = alias
		if phone != "":
			self.phone = phone
		self.date_created = datetime.now().isoformat()
		if password:
			self.set_password(password)
		else:
			self.set_password(app.config['ADMIN_PASSWORD'])
		self.department = department
	def __repr__(self):
		return '<User %r>' % self.email
	def __str__(self):
		return self.email
	def department_name(self):
		if self.current_department and self.current_department.name:
			return self.current_department.name
		else:
			app.logger.error("\n\nUser %s is not associated with a department." % self.email)
			return "N/A"

### @export "Department"
class Department(db.Model):
	__tablename__ = 'department'
	id = db.Column(db.Integer, primary_key =True)
	date_created = db.Column(db.DateTime)
	date_updated = db.Column(db.DateTime)
	name = db.Column(db.String(), unique=True)
	users = relationship("User") # The list of users in this department
	requests = relationship("Request", order_by = "Request.date_created.asc()") # The list of requests currently associated with this department
	def __init__(self, name):
		self.name = name
		self.date_created = datetime.now().isoformat()
	def __repr__(self):
		return '<Department %r>' % self.name
	def __str__(self):
		return self.name
	def get_name(self):
		return self.name or "N/A"

### @export "Request"
class Request(db.Model): 
# The public records request
	__tablename__ = 'request'
	id = db.Column(db.Integer, primary_key =True)
	date_created = db.Column(db.DateTime)
	due_date = db.Column(db.DateTime)
	extended = db.Column(db.Boolean, default = False) # Has the due date been extended?
	qas = relationship("QA", cascade="all,delete", order_by = "QA.date_created.desc()") # The list of QA units for this request
	status_updated = db.Column(db.DateTime)
	text = db.Column(db.String(), unique=True) # The actual request text.
	owners = relationship("Owner", cascade = "all, delete", order_by="Owner.date_created.asc()")
	subscribers = relationship("Subscriber", cascade ="all, delete") # The list of subscribers following this request.
	current_owner = db.Column(Integer) # Deprecated
	records = relationship("Record", cascade="all,delete", order_by = "Record.date_created.desc()") # The list of records that have been uploaded for this request.
	notes = relationship("Note", cascade="all,delete", order_by = "Note.date_created.desc()") # The list of notes appended to this request.
	status = db.Column(db.String(400)) # The status of the request (open, closed, etc.)
	creator_id = db.Column(db.Integer, db.ForeignKey('user.id')) # If city staff created it on behalf of the public, otherwise the creator is the subscriber with creator = true
	department = db.Column(db.String())
	department_id = db.Column(db.Integer, db.ForeignKey("department.id"))
	department_obj = relationship("Department", uselist = False)
	date_received = db.Column(db.DateTime)
	offline_submission_type = db.Column(db.String())

	def __init__(self, text, creator_id = None, department = None, offline_submission_type = None, date_received = None):
		self.text = text
		self.date_created = datetime.now().isoformat()
		self.creator_id = creator_id
		self.department = department
		self.offline_submission_type = offline_submission_type
		self.date_received = date_received
		self.due_date = datetime.now() + timedelta(days = int(app.config['DAYS_TO_FULFILL']))

	def __repr__(self):
		return '<Request %r>' % self.text

	def set_due_date(self):
		self.due_date = self.date_created + timedelta(days = int(app.config['DAYS_TO_FULFILL']))
		if self.extension:
				self.due_date = self.due_date + timedelta(days = int(app.config['DAYS_AFTER_EXTENSION']))

	def extension(self):
		self.extended = True 
		self.due_date = self.due_date + timedelta(days = int(app.config['DAYS_AFTER_EXTENSION']))
	def point_person(self):
		for o in self.owners:
			if o.is_point_person:
				return o
		return None
	def requester(self):
		if self.subscribers:
			return self.subscribers[0] or None # The first subscriber is always the requester
		return None

	def requester_name(self):
		requester = self.requester()
		if requester and requester.user:
			return requester.user.get_alias()
		return "N/A"
	def point_person_name(self):
		point_person = self.point_person()
		if point_person and point_person.user:
			return point_person.user.get_alias()
		return "N/A"
	def department_name(self):
		if self.department_obj:
			return self.department_obj.get_name()
		return "N/A"
	def is_closed(self):
		return re.match('.*(closed).*', self.status, re.IGNORECASE) is not None
	def solid_status(self, cron_job = False):
		if self.is_closed():
			return "closed"
		else:
			if cron_job or (not current_user.is_anonymous()):
				if datetime.now() >= self.due_date:
					return "overdue"
				elif (datetime.now() + timedelta(days = 2)) >= self.due_date:
					return "due soon"
		return "open"

### @export "QA"
class QA(db.Model):
# A Q & A block for a request
	__tablename__ = 'qa'
	id = db.Column(db.Integer, primary_key = True)
	question = db.Column(db.String())
	answer = db.Column(db.String())
	request_id = db.Column(db.Integer, db.ForeignKey('request.id'))
	owner_id = db.Column(db.Integer, db.ForeignKey('user.id')) # Actually just a user ID
	subscriber_id = db.Column(db.Integer, db.ForeignKey('user.id')) # Actually just a user ID
	date_created = db.Column(db.DateTime)
	def __init__(self, request_id, question, owner_id = None):
		self.question = question
		self.request_id = request_id
		self.date_created = datetime.now().isoformat()
		self.owner_id = owner_id
	def __repr__(self):
		return "<QA Q: %r A: %r>" %(self.question, self.answer)

### @export "Owner"
class Owner(db.Model): 
# A member of city staff assigned to a particular request, that may or may not upload records towards that request.
	__tablename__ = 'owner'
	id = db.Column(db.Integer, primary_key =True)
	user_id = Column(Integer, ForeignKey('user.id'))
	user = relationship("User", uselist = False)
	request_id = db.Column(db.Integer, db.ForeignKey('request.id'))
	request = relationship("Request", foreign_keys = [request_id])
	active = db.Column(db.Boolean, default = True) # Indicate whether they're still involved in the request or not.
	reason = db.Column(db.String()) # Reason they were assigned
	reason_unassigned = db.Column(db.String()) # Reason they were unassigned
	date_created = db.Column(db.DateTime)
	date_updated = db.Column(db.DateTime)
	is_point_person = db.Column(db.Boolean)
	def __init__(self, request_id, user_id, reason= None, is_point_person = False):
		self.reason = reason
		self.user_id = user_id
		self.request_id = request_id
		self.date_created = datetime.now().isoformat()
		self.date_updated = self.date_created
		self.is_point_person = is_point_person
	def __repr__(self):
		return '<Owner %r>' %self.user_id

### @export "Subscriber"
class Subscriber(db.Model): 
# A person subscribed to a request, who may or may not have created the request, and may or may not own a part of the request.
	__tablename__ = 'subscriber'
	id = db.Column(db.Integer, primary_key = True)
	should_notify = db.Column(db.Boolean, default = True) # Allows a subscriber to unsubscribe
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
	user = relationship("User", uselist = False)
	request_id = db.Column(db.Integer, db.ForeignKey('request.id'))
	date_created = db.Column(db.DateTime)
	owner_id = db.Column(db.Integer, db.ForeignKey('owner.id')) # Not null if responsible for fulfilling a part of the request
 	def __init__(self, request_id, user_id, creator = False):
 		self.user_id = user_id
		self.request_id = request_id
		self.date_created = datetime.now().isoformat()
	def __repr__(self):
		return '<Subscriber %r>' %self.user_id

### @export "Record"
class Record(db.Model):
# A record that is attached to a particular request. A record can be online (uploaded document, link) or offline.
	__tablename__ = 'record'
	id = db.Column(db.Integer, primary_key = True)
	date_created = db.Column(db.DateTime)
	user_id = db.Column(db.Integer, db.ForeignKey('user.id')) # The user who uploaded the record, right now only city staff can
	doc_id = db.Column(db.Integer) # The document ID. Currently using Scribd API to upload documents.
	request_id = db.Column(db.Integer, db.ForeignKey('request.id')) # The request this record was uploaded for
	description = db.Column(db.String(400)) # A short description of what the record is. 
	filename = db.Column(db.String(400)) # The original name of the file being uploaded.
	url = db.Column(db.String()) # Where it exists on the internet.
	download_url = db.Column(db.String()) # Where it can be downloaded on the internet.
	access = db.Column(db.String()) # How to access it. Probably only defined on offline docs for now.
	def __init__(self, request_id, user_id, url = None, filename = None, doc_id = None, description = None, access = None):
		self.doc_id = doc_id
		self.request_id = request_id
		self.user_id = user_id
		self.date_created = datetime.now().isoformat()
		self.description = description
		self.url = url
		self.filename = filename
		self.access = access
	def __repr__(self):
		return '<Record %r>' % self.description

### @export "Note"
class Note(db.Model):
# A note on a request.
	__tablename__ = 'note'
	id = db.Column(db.Integer, primary_key = True)
	date_created = db.Column(db.DateTime)
	text = db.Column(db.String())
	request_id = db.Column(db.Integer, db.ForeignKey('request.id')) # The request it belongs to.
	user_id = db.Column(db.Integer, db.ForeignKey('user.id')) # The user who wrote the note. Right now only city staff can.
	def __init__(self, request_id, text, user_id):
		self.text = text
		self.request_id = request_id
		self.user_id = user_id
		self.date_created = datetime.now().isoformat()
	def __repr__(self):
		return '<Note %r>' % self.text

### @export "Visualization"
class Visualization(db.Model):
	__tablename__ = 'visualization'
	id = db.Column(db.Integer, primary_key = True)
	content = db.Column(db.String())
	date_created = db.Column(db.DateTime)
	date_updated = db.Column(db.DateTime)
	type_viz = db.Column(db.String())
	def __init__(self, type_viz, content):
		self.type_viz = type_viz
		self.content = content
		self.date_created = datetime.now().isoformat()
	def __repr__(self):
		return '<Visualization %r>' % self.type_viz
