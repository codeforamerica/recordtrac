from flask import Flask, render_template, request, flash
from upload import upload
from flask.ext.sqlalchemy import SQLAlchemy
# from flask.ext.sqlalchemy.exceptions import *
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://localhost/mydatabase'
db = SQLAlchemy(app)
db.create_all()
from models import *


@app.route('/test')
def sandbox():
	return render_template('test.html')

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
    		if owner.doc_id:
    			doc_ids.append(owner.doc_id)
    		else:
    			doc_ids.append("Nothing uploaded yet by %s" % owner.name)
    return render_template('requested.html', text = r.text, request_id = request_id, doc_ids = doc_ids, status = r.status)



# @app.route('/request/edit/<int:request_id>', methods=['GET', 'POST'])
# def edit_request(request_id):
# 	if request.method == 'POST':
# 		owner_id = request.form['owner_id']
# 		db.session.delete(Owner.query.get(owner_id))
# 	# edit the request with the given id
# 	owner_ids = []
# 	owner_emails = []
# 	req = Request.query.get(request_id)
# 	if req.owners:
# 		for owner in req.owners:
# 			owner_ids.append(owner.id)
# 			owner_emails.append(owner.email)

def assign_owner(request_id, name, email):
	contact = Contact(email)
	db.session.add(contact)
	owner = Owner(name, id)
	owner.contact_id = contact.id
	owner.request_id = request_id
	db.session.add(owner)
	db.session.commit()
	return owner.id

def unassign_owner(owner_id):
	owner = Owner.query.get(owner_id)
	db.session.delete(owner)
	db.session.commit()


# def view_owner(id):
# 	owner = owner.query.get(id)
# 	print "Owner"

def make_request(str):
	try:
		req = Request(str)
		db.session.add(req)
		db.session.commit()
		owner_id = assign_owner(req.id, "richa", "richa@codeforamerica.org")
		# unassign_owner(owner_id)
		open_request(req.id)
		return req.id
	except:
		return None
	# except exc.InvalidRequestError:
	# 	return None



def change_request_status(id, status):
	try:
		req = Request.query.get(id)
		req.status = status
		db.session.commit()
		return True
	except:
		return False

def notify(id):
	req = Request.query.get(id)
	if len(req.owners) != 0:
		owner = req.owners[0]
		print "This is the e-mail we would send to owner %s" % owner.name
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

