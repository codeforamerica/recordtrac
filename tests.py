import os
from public_records_portal import app, prflask, models
import unittest
import random, string
import tempfile
import flask

class PublicRecordsTestCase(unittest.TestCase):

	def random_content(self, content_type):
		return "This is a new %s and some random string %s" %(content_type, ''.join(random.choice(string.lowercase) for i in range(10)))

	def test_filters(self):
		with app.test_request_context('/requests?closed=false'):
			assert flask.request.path == '/requests'
			assert flask.request.args['closed'] == 'false'

	def logout(self):
		return self.app.post('/logout')

	def login(self):
		with app.test_client() as c:
			with c.session_transaction() as sess:
				sess['user_id'] = 1
				sess['_fresh'] = True # http://pythonhosted.org/Flask-Login/#fresh-logins
		# resp = c.get('/someurl')

	def setUp(self):
		models.db.drop_all() # Start with a fresh database
		self.app = app.test_client()
		models.db.create_all()

	def tearDown(self):
		models.db.session.remove()
		models.db.drop_all() # Clear out this session

	# def test_index_logged_out(self):
	# 	page = self.app.get('/', follow_redirects= True)
	# 	assert 'Submit a Request' in page.data



	def test_submit_request(self):
		request = self.random_content('request')
		page = self.submit_request(text= request,email = 'richa@richa.com')
		assert request in page.data

	def test_new(self):
		page = self.app.get('/new')
		assert 'Request a new record' in page.data

	# def test_ask_question(self):
	# 	self.login()
	# 	question = self.random_content('question')
	# 	fields = dict(request_id = 5, question_text = question)
	# 	page = self.submit_generic(fields = fields, endpoint = "add_a_qa")
	# 	self.logout()
	# 	assert question in page.data

	# def test_answer_question(self):
	# 	answer = self.random_content('answer')
	# 	fields = dict(request_id = 5, qa_id = 15, user_id = 2, answer_text = answer)
	# 	page = self.submit_generic(fields = fields, endpoint = "update_a_qa")
	# 	assert answer in page.data

	def test_add_note(self):
		self.login()
		self.submit_request(text=self.random_content('request'), email = 'richa@richa.com')
		note_text = self.random_content('note')
		fields = dict(request_id = 1, note_text = note_text)
		page = self.submit_generic(fields = fields, endpoint = "add_a_note")
		self.logout()
		assert note_text in page.data

	def test_public_add_note(self):
		self.submit_request(text=self.random_content('request'), email = 'richa@richa.com')
		note_text = self.random_content('note')
		fields = dict(request_id = 1, note_text = note_text)
		page = self.submit_generic(fields = fields, endpoint = "public_add_a_note")
		assert note_text in page.data

	def test_add_offline_doc(self):
		self.login()
		self.submit_request(text=self.random_content('request'), email = 'richa@richa.com')
		record_description = self.random_content('record description')
		record_access = self.random_content('record access')
		fields = dict(request_id = 1, record_description = record_description, record_access = record_access)
		page = self.submit_generic(fields = fields, endpoint = "add_a_record")
		self.logout()
		assert record_access in page.data

	def test_add_link(self):
		self.login()
		self.submit_request(text=self.random_content('request'), email = 'richa@richa.com')
		link_description = self.random_content('link description')
		link_url = 'http://www.google.com'
		fields = dict(request_id = 1, record_description = link_description, link_url = link_url)
		page = self.submit_generic(fields = fields, endpoint = "add_a_record")
		self.logout()
		assert link_description in page.data

	def test_close_request(self):
		request = self.random_content('request')
		self.submit_request(text= request,email = 'richa@richa.com')
		self.login()
		close_reason = self.random_content('close reason')
		fields = dict(request_id = 1, close_reason = close_reason)
		page = self.submit_generic(fields = fields, endpoint = "close")
		self.logout()
		assert close_reason in page.data

	def test_submit_duplicate_request(self):
		request = 'this is a duplicate request'
		page1 = self.submit_request('richa@richa.com', request)
		page2 = self.submit_request('richa@richa.com', request)
		assert 'Your request is the same as' in page2.data

	def test_reroute_owner(self):
		self.submit_request(text= self.random_content('request'), email = 'richa@richa.com')
		self.login()
		reroute_reason = self.random_content('reroute reason')
		fields = dict(request_id = 1, owner_reason = reroute_reason, owner_email = "cris@codeforamerica.org")
		page = self.submit_generic(fields = fields, endpoint = "update_a_owner")
		self.logout()
		assert reroute_reason in page.data


	def submit_request(self, email, text):
		return self.app.post('/new', data=dict(
		request_text= text,
		request_email = email
	), follow_redirects=True)

	def submit_generic(self, fields, endpoint = ""):
		return self.app.post('/%s' % (endpoint), data = fields, follow_redirects= True)

if __name__ == '__main__':
	unittest.main()