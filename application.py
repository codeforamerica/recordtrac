import os
from werkzeug import secure_filename
from flask import Flask, render_template, request, flash, redirect, url_for
from upload import upload
from flask.ext.sqlalchemy import SQLAlchemy
UPLOAD_FOLDER = "%s/uploads" % os.getcwd()
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'doc'])
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://localhost/mydatabase'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
db = SQLAlchemy(app)
db.create_all()
from models import *


@app.route('/test')
def sandbox():
	return render_template('test.html')

def allowed_file(filename):
	return '.' in filename and \
		filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['GET', 'POST'])
def load():
	if request.method == 'POST':
		doc_id = -1
		file = request.files['record']
		if file and allowed_file(file.filename):
			filename = secure_filename(file.filename)
			filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
			file.save(filepath)
			doc_id = upload(filepath)
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
    if r.records:
    	for record in r.records:
    		if record.scribd_id:
    			doc_ids.append(record.scribd_id)
    		else:
    			doc_ids.append("Nothing uploaded yet by %s" % owner.name)
    return render_template('requested.html', text = r.text, request_id = request_id, doc_ids = doc_ids, status = r.status)


def assign_owner(request_id, name, email):
	subscriber = Subscriber(request_id = request_id, alias = name, email = email)
	db.session.add(subscriber)
	owner = Owner(alias = subscriber.alias, email = subscriber.email)
	db.session.add(owner)
	subscriber.owner_id = owner.id
	db.session.commit()
	return owner.id

def unassign_owner(subscriber_id):
	subscriber = Subscriber.query.get(subscriber_id)
	if subscriber.owner_id:
		owner = Owner.query.get(subscriber.owner_id)
		db.session.delete(owner)
		db.session.commit()
		return True # Unassigned successfully
	return False # No one to unassign

def make_request(str):
	try:
		req = Request(str)
		db.session.add(req)
		db.session.commit()
		owner_id = assign_owner(req.id, "richa", "richa@codeforamerica.org")
		open_request(req.id)
		return req.id
	except:
		return None

def change_request_status(id, status):
	try:
		req = Request.query.get(id)
		req.status = status
		db.session.commit()
		return True
	except:
		return False

def get_owners(request_id):
	req = Request.query.get(request_id)
	subscribers = req.subscribers
	for subscriber in subscribers:
		if subscriber.owner_id != null:
			yield subscriber.owner_id

def notify(request_id):
	req = Request.query.get(request_id)
	subscribers = req.subscribers
	if len(subscribers) != 0:
		for subscriber in subscribers:
			print "This is the e-mail we would send to owner %s" % subscriber.alias
			print "Subject: Request for %s is now %s" % (req.text, req.status)
	else:
		print "No one assigned!"


def open_request(id):
	change_request_status(id, "Open")
	notify(id)

def close_request(id):
	change_request_status(id, "Closed")
	notify(id)


@app.route('/', methods=['GET', 'POST'])
def index():
	if request.method == 'POST':
		request_text = request.form['request_text']
		request_id = make_request(request_text)
		if request_id:
			return show_request(request_id)
		else:
			req = Request.query.filter_by(text = request_text).first()
			return render_template('error.html', message = "Your request is the same as /request/%s" % req.id)
	return render_template('index.html')

@app.route('/requests', methods=['GET', 'POST'])
def requests():
	all_record_requests = Request.query.all()
	return render_template('requests.html', all_record_requests = all_record_requests)

if __name__ == '__main__':
	app.run(use_debugger=True, debug=True)

