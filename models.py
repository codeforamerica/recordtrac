from prflask import db
from sqlalchemy.orm import relationship
from datetime import datetime

class Request(db.Model): 
# The public records request
	__tablename__ = 'request'
	id = db.Column(db.Integer, primary_key =True)
	date_created = db.Column(db.DateTime)
	status_updated = db.Column(db.DateTime)
	text = db.Column(db.String(400), unique=True) # The actual request text.
	subscribers = relationship("Subscriber") # The list of subscribers following this request.
	owners = relationship("Owner") # The list of city staff ever assigned to the request.
	current_owner = db.Column(db.Integer) # The Owner ID for the city staff that currently 'owns' the request.
	records = relationship("Record") # The list of records that have been uploaded for this request.
	notes = relationship("Note") # The list of notes appended to this request.
	status = db.Column(db.String(400)) # The status of the request (open, closed, etc.)
	def __init__(self, text):
		self.text = text
		self.date_created = datetime.now()
	def __repr__(self):
		return self.text

class Owner(db.Model): 
# A member of city staff assigned to a particular request, that may or may not upload records towards that request. 
	__tablename__ = 'owner'
	id = db.Column(db.Integer, primary_key =True)
	alias = db.Column(db.String(20))
	email = db.Column(db.String(100))
	date_created = db.Column(db.DateTime)
	records = relationship("Record") # All records that have been uploaded
	request_id = db.Column(db.Integer, db.ForeignKey('request.id'))
	reason = db.Column(db.String(400)) # Reason they were assigned
	def __init__(self, request_id, email, reason= None, alias = None):
		self.reason = reason
		self.alias = alias
		self.email = email
		self.request_id = request_id
		self.date_created = datetime.now()
	def __repr__(self):
		return self.alias


class Subscriber(db.Model): 
# A person subscribed to a request, who may or may not have created the request, and may or may not own a part of the request.
	__tablename__ = 'subscriber'
	id = db.Column(db.Integer, primary_key = True)
	email = db.Column(db.String(100))
	alias = db.Column(db.String(20))
	date_created = db.Column(db.DateTime)
	request_id = db.Column(db.Integer, db.ForeignKey('request.id'))
	creator = db.Boolean() # True if they created the initial request.
	owner_id = db.Column(db.Integer, db.ForeignKey('owner.id')) # Not null if responsible for fulfilling a part of the request
 	def __init__(self, request_id, email, alias = None):
 		self.email = email
 		self.alias = alias
		self.request_id = request_id
		self.date_created = datetime.now()
	def __repr__(self):
		return self.alias


class Record(db.Model):
# A record that has been uploaded for a request.
	__tablename__ = 'record'
	id = db.Column(db.Integer, primary_key = True)
	date_created = db.Column(db.DateTime)
	owner_id = db.Column(db.Integer, db.ForeignKey('owner.id')) # The city staff who uploaded the record
	doc_id = db.Column(db.Integer) # The document ID. Currently using Scribd API to upload documents.
	request_id = db.Column(db.Integer, db.ForeignKey('request.id')) # The request this record was uploaded for
	description = db.Column(db.String(100)) # A short description of what the record is. 
	filename = db.Column(db.String(100)) # The original name of the file being uploaded.
	url = db.Column(db.String(200)) # Where it exists on the internet.
	def __init__(self, request_id, owner_id, url = None, doc_id = None, description = None):
		self.doc_id = doc_id
		self.request_id = request_id
		self.owner_id = owner_id
		self.date_created = datetime.now()
		self.description = description
		self.url = url
	def __repr__(self):
		return self.records

class Note(db.Model):
# A note on a request.
	__tablename__ = 'note'
	id = db.Column(db.Integer, primary_key = True)
	date_created = db.Column(db.DateTime)
	text = db.Column(db.String(400))
	request_id = db.Column(db.Integer, db.ForeignKey('request.id')) # The request it belongs to.
	subscriber_id = db.Column(db.Integer, db.ForeignKey('subscriber.id')) # The subscriber who wrote the note
	owner_id = db.Column(db.Integer, db.ForeignKey('owner.id'))
	def __init__(self, request_id, text, subscriber_id = None, owner_id = None):
		self.text = text
		self.request_id = request_id
		self.subscriber_id = subscriber_id
		self.owner_id = owner_id
		self.date_created = datetime.now()
	def __repr__(self):
		return self.text

