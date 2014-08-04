import os
from public_records_portal import app, prflask, models, prr
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

	def setUp(self):
		models.db.drop_all() # Start with a fresh database
		self.app = app.test_client()
		models.db.create_all()

	def tearDown(self):
		models.db.session.remove()
		models.db.drop_all() # Clear out this session

	def test_submit_request(self):
		request = self.random_content('request')
		page = self.app.post('/new', data=dict(
		request_text= request,
		request_email = 'richa@richa.com'), follow_redirects=True)
		assert request in page.data

	def test_new(self):
		page = self.app.get('/new')
		assert 'Request a new record' in page.data

	def test_ask_question(self):
		question = self.random_content('question')
		page = self.ask_question(question)
		assert question in page.data

	def ask_question(self, question):
		request_id = self.submit_request(text=self.random_content('request'), email = 'richa@richa.com')
		fields = dict(request_id = request_id, question_text = question)
		page = self.submit_generic(fields = fields, endpoint = "add_a_qa")
		return page

	def test_answer_question(self):
		request_id = self.submit_request(text=self.random_content('request'), email = 'richa@richa.com')
		qa_id = prr.ask_a_question(request_id = request_id, user_id = 1, question  = self.random_content('question'))
		answer = self.random_content('answer')
		fields = dict(request_id = request_id, qa_id = qa_id, user_id = 1, answer_text = answer)
		page = self.submit_generic(fields = fields, endpoint = "update_a_qa")
		assert answer in page.data

	def test_public_add_note(self):
		request_id = self.submit_request(text=self.random_content('request'), email = 'richa@richa.com')
		note_text = self.random_content('note')
		fields = dict(request_id = request_id, note_text = note_text)
		page = self.submit_generic(fields = fields, endpoint = "public_add_a_note")
		assert note_text in page.data

	# Tests for adding a record: 
	# ---

	# This doesn't test Scribd, but tests the rest of the workflow:
	def test_upload_record(self):
		request_id = self.submit_request(text=self.random_content('request'), email = 'richa@richa.com')
		record_description = self.random_content('record')
		fields = dict(request_id = request_id, record_description = record_description)
		page = self.submit_generic(fields = fields, endpoint = "add_a_record")
		assert record_description in page.data
		
	def test_add_note(self):
		request_id = self.submit_request(text=self.random_content('request'), email = 'richa@richa.com')
		note_text = self.random_content('note')
		fields = dict(request_id = request_id, note_text = note_text)
		page = self.submit_generic(fields = fields, endpoint = "add_a_note")
		assert note_text in page.data

	def test_add_offline_doc(self):
		request_id = self.submit_request(text=self.random_content('request'), email = 'richa@richa.com')
		record_description = self.random_content('record description')
		record_access = self.random_content('record access')
		fields = dict(request_id = request_id, record_description = record_description, record_access = record_access)
		page = self.submit_generic(fields = fields, endpoint = "add_a_record")
		assert record_access in page.data

	def test_add_link(self):
		request_id = self.submit_request(text=self.random_content('request'), email = 'richa@richa.com')
		link_description = self.random_content('link description')
		link_url = 'http://www.google.com'
		fields = dict(request_id = request_id, record_description = link_description, link_url = link_url)
		page = self.submit_generic(fields = fields, endpoint = "add_a_record")
		assert link_description in page.data
	# ---

	def test_close_request(self):
		request = self.random_content('request')
		self.submit_request(text= request,email = 'richa@richa.com')
		close_reason = self.random_content('close reason')
		fields = dict(request_id = 1, close_reason = close_reason)
		page = self.submit_generic(fields = fields, endpoint = "close")
		assert close_reason in page.data

	def test_reroute_owner(self):
		request_id = self.submit_request(text= self.random_content('request'), email = 'richa@richa.com')
		reroute_reason = self.random_content('reroute reason')
		fields = dict(request_id = request_id, owner_reason = reroute_reason, owner_email = "cris@codeforamerica.org")
		page = self.submit_generic(fields = fields, endpoint = "update_a_owner")
		assert reroute_reason in page.data


	def submit_request(self, email, text):
		request_id, success = prr.make_request(text = text, email = email, passed_spam_filter = True)
		return request_id

	def submit_generic(self, fields, endpoint = ""):
		return self.app.post('/%s' % (endpoint), data = fields, follow_redirects= True)

if __name__ == '__main__':
	unittest.main()