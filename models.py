from application import db
from sqlalchemy.orm import relationship

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    email = db.Column(db.String(120), unique=True)

    def __init__(self, username, email):
        self.username = username
        self.email = email

    def __repr__(self):
        return '<User %r>' % self.username

class Request(db.Model):
	__tablename__ = 'request'
	id = db.Column(db.Integer, primary_key =True)
	text = db.Column(db.String(400), unique=True)
	owners = relationship("Owner")
	status = db.Column(db.String(400))
	def __init__(self, text):
		self.text = text
	def __repr__(self):
		return self.text

class Owner(db.Model):
	__tablename__ = 'owner'
	id = db.Column(db.Integer, primary_key =True)
	name = db.Column(db.String(20))
	doc_id = db.Column(db.Integer)
	request_id = db.Column(db.Integer, db.ForeignKey('request.id'))
	def __init__(self, name, request_id):
		self.name = name
		self.request_id = request_id
	def __repr__(self):
		return self.name