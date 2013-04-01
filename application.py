from flask import Flask, render_template, request, flash
from upload import upload
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://localhost/mydatabase'
db = SQLAlchemy(app)
db.create_all()

@app.route('/upload', methods=['GET', 'POST'])
def load():
	if request.method == 'POST':
		doc_id = upload(request.form['filepath'])
		request_id = request.form['request_id']
		owner = Owner('anon', request_id)
		owner.doc_id = int(doc_id)
		db.session.add(owner)
		db.session.commit()
		return render_template('uploaded.html', doc_id = doc_id)
	else:
		return render_template('error.html')

@app.route('/request/<int:request_id>')
def show_request(request_id):
    # show the request with the given id, the id is an integer
    r = Request.query.get(request_id)
    doc_ids = []
    if r.owners:
    	for owner in r.owners:
    		doc_ids.append(owner.doc_id)
    return render_template('requested.html', text = r.text, request_id = request_id, doc_ids = doc_ids)


@app.route('/', methods=['GET', 'POST'])
def index():
	if request.method == 'POST':
		text = request.form['request_text']
		record_request = Request(text)
		db.session.add(record_request)
		db.session.commit()
		request_id = record_request.id
		return show_request(request_id)
	else:
		return render_template('index.html')

@app.route('/requests', methods=['GET', 'POST'])
def requests():
	all_record_requests = Request.query.all()
	return render_template('requests.html', all_record_requests = all_record_requests)


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



if __name__ == '__main__':
	app.run(use_debugger=True, debug=True)

