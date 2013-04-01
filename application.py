from flask import Flask, render_template, request, flash
from models import *
from upload import upload
from flask.ext.sqlalchemy import SQLAlchemy
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://localhost/mydatabase'
db = SQLAlchemy(app)
db.create_all()


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
    		doc_ids.append(owner.doc_id)
    return render_template('requested.html', text = r.text, request_id = request_id, doc_ids = doc_ids, status = r.status)

def make_request(str):
	req = Request(str)
	db.session.add(req)
	db.session.commit()
	open_request(req.id)
	return req.id

def change_request_status(id, status):
	try:
		req = Request.query.get(id)
		req.status = status
		db.session.commit()
		return True
	except:
		return False

def open_request(id):
	notify(id, status)
	return change_request_status(id, "Open")

def close_request(id):
	return change_request_status(id, "Closed")

@app.route('/', methods=['GET', 'POST'])
def index():
	if request.method == 'POST':
		text = request.form['request_text']
		request_id = make_request(text)
		return show_request(request_id)
	else:
		return render_template('index.html')

@app.route('/requests', methods=['GET', 'POST'])
def requests():
	all_record_requests = Request.query.all()
	return render_template('requests.html', all_record_requests = all_record_requests)



if __name__ == '__main__':
	app.run(use_debugger=True, debug=True)

