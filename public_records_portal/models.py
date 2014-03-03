from flask.ext.sqlalchemy import SQLAlchemy, sqlalchemy

from sqlalchemy import Table, Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method

from datetime import datetime
from public_records_portal import db
from werkzeug.security import generate_password_hash, check_password_hash
import json
import re

Base = db.Model

### @export "User"
class User(Base):
        __tablename__ = 'user'

	id = db.Column(db.Integer, primary_key = True)

	alias = db.Column(db.String(100))
	email = db.Column(db.String(100), unique=True)
	phone = db.Column(db.String())
	date_created = db.Column(db.DateTime)
	password = db.Column(db.String(255))
	department = db.Column(db.String())
	contact_for = db.Column(db.String()) # comma separated list
	backup_for = db.Column(db.String()) # comma separated list
        owners = relationship("Owner")

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
	def __init__(self, email=None, alias = None, phone=None, department = None, password=None):
		self.email = email
		self.alias = alias
		self.phone = phone
		self.date_created = datetime.now().isoformat()
		self.set_password(password)
		self.department = department
	def __repr__(self):
		return '<User %r>' % self.email

### @export "Request"
class Request(Base): 
# The public records request
	__tablename__ = 'request'
	id = db.Column(db.Integer, primary_key =True)
	date_created = db.Column(db.DateTime)
	extended = db.Column(db.Boolean, default = False) # Has the due date been extended?
	qas = relationship("QA", cascade="all,delete", order_by = "QA.date_created.desc()") # The list of QA units for this request
	status_updated = db.Column(db.DateTime)
	text = db.Column(db.String(), unique=True) # The actual request text.
	subscribers = relationship("Subscriber", cascade ="all, delete") # The list of subscribers following this request.

	owners = relationship("Owner", cascade="all,delete") # The list of city staff ever assigned to the request.
	current_owner = Column(Integer) # The Owner ID for the city staff that currently 'owns' the request.
        point_person = relationship("Owner", uselist=False)

	records = relationship("Record", cascade="all,delete", order_by = "Record.date_created.desc()") # The list of records that have been uploaded for this request.
	notes = relationship("Note", cascade="all,delete", order_by = "Note.date_created.desc()") # The list of notes appended to this request.
	status = db.Column(db.String(400)) # The status of the request (open, closed, etc.)
	creator_id = db.Column(db.Integer, db.ForeignKey('user.id')) # If city staff created it on behalf of the public, otherwise the creator is the subscriber with creator = true
	department = db.Column(db.String())
	def __init__(self, text, creator_id = None, department = None):
		self.text = text
		self.date_created = datetime.now().isoformat()
		self.creator_id = creator_id
		self.department = department
	def __repr__(self):
		return '<Request %r>' % self.text
        def contact_name(self):
                return self.point_person.user.alias

        def is_closed(self):
                return re.match('.*(closed).*', self.status) is not None

### @export "QA"
class QA(Base):
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
class Owner(Base): 
# A member of city staff assigned to a particular request, that may or may not upload records towards that request.
	__tablename__ = 'owner'
	id = db.Column(db.Integer, primary_key =True)

	user_id = Column(Integer, ForeignKey('user.id'))
        user = relationship("User")

	request_id = db.Column(db.Integer, db.ForeignKey('request.id'))
	reason = db.Column(db.String()) # Reason they were assigned
	date_created = db.Column(db.DateTime)
	def __init__(self, request_id, user_id, reason= None):
		self.reason = reason
		self.user_id = user_id
		self.request_id = request_id
		self.date_created = datetime.now().isoformat()
	def __repr__(self):
		return '<Owner %r>' %self.user_id

### @export "Subscriber"
class Subscriber(Base): 
# A person subscribed to a request, who may or may not have created the request, and may or may not own a part of the request.
	__tablename__ = 'subscriber'
	id = db.Column(db.Integer, primary_key = True)
	should_notify = db.Column(db.Boolean, default = True) # Allows a subscriber to unsubscribe
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
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
class Record(Base):
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
class Note(Base):
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
class Visualization(Base):
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
