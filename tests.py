import os
from public_records_portal.prflask import app
import unittest
import random, string


class PublicRecordsTestCase(unittest.TestCase):

	def random_content(self, content_type):
		return "This is a new %s and some random string %s" %(content_type, ''.join(random.choice(string.lowercase) for i in range(10)))

	def login(self):
		return self.app.post('/login', data=dict(
        email='email',
        password='password'
    ), follow_redirects=True)

	def logout(self):
		return self.app.post('/logout')

	def setUp(self):
		self.app = app.test_client()

	def test_route_request(self):
		self.login()
		reason = self.random_content('reason')
		fields = dict(request_id = 5, owner_email = "richa@codeforamerica.org", owner_reason = reason)
		page = self.submit_generic(fields = fields, endpoint = "update_a_owner")
		self.logout()
		assert reason in page.data

	def test_index_logged_in(self):
		self.login()
		page = self.app.get('/', follow_redirects= True)
		self.logout()
		assert 'Requests assigned to you' in page.data

	def test_index_logged_out(self):
		page = self.app.get('/', follow_redirects= True)
		assert 'Submit a Request' in page.data

	def test_empty_db(self):
		page = self.app.get('/requests')
		assert 'No entries here so far' in page.data

	def test_not_empty_db(self):
		page = self.app.get('/requests')
		assert 'All Requests' in page.data

	def test_not_empty_db_city(self):
		self.login()
		page = self.app.get('/your_requests')
		assert "Requests assigned to you" in page.data
		self.logout()

	def test_submit_request(self):
		request = self.random_content('request')
		page = self.submit_request('richa@richa.com', request)
		assert request in page.data

	def test_home(self):
		page = self.app.get('/')
		assert 'Submit a Request' in page.data

	def test_ask_question(self):
		self.login()
		question = self.random_content('question')
		fields = dict(request_id = 5, question_text = question)
		page = self.submit_generic(fields = fields, endpoint = "add_a_qa")
		self.logout()
		assert question in page.data

	def test_answer_question(self):
		answer = self.random_content('answer')
		fields = dict(request_id = 5, qa_id = 15, user_id = 2, answer_text = answer)
		page = self.submit_generic(fields = fields, endpoint = "update_a_qa")
		assert answer in page.data

	def test_add_note(self):
		self.login()
		note_text = self.random_content('note')
		fields = dict(request_id = 5, note_text = note_text)
		page = self.submit_generic(fields = fields, endpoint = "add_a_note")
		self.logout()
		assert note_text in page.data

	def test_add_offline_doc(self):
		self.login()
		record_description = self.random_content('record description')
		record_access = self.random_content('record access')
		fields = dict(request_id = 5, record_description = record_description, record_access = record_access)
		page = self.submit_generic(fields = fields, endpoint = "add_a_record")
		self.logout()
		assert record_access in page.data

	def test_add_link(self):
		self.login()
		link_description = self.random_content('link description')
		link_url = 'http://www.google.com'
		fields = dict(request_id = 5, record_description = link_description, link_url = link_url)
		page = self.submit_generic(fields = fields, endpoint = "add_a_record")
		self.logout()
		assert link_description in page.data

	def test_close_request(self):
		self.login()
		close_reason = self.random_content('close reason')
		fields = dict(request_id = 4, close_reason = close_reason)
		page = self.submit_generic(fields = fields, endpoint = "close")
		self.logout()
		assert close_reason in page.data

	def test_submit_duplicate_request(self):
		request = 'this is a duplicate request'
		page = self.submit_request('richa@richa.com', request)
		assert 'Your request is the same as' in page.data

	def test_all_requests_logged_in(self):
		self.login()
		page = self.app.get('/requests')
		self.logout()
		assert '/city/request/' in page.data

	def test_all_requests_logged_out(self):
		page = self.app.get('/requests')
		assert '/request/' in page.data

	def test_reroute_owner(self):
		self.login()
		reroute_reason = self.random_content('reroute reason')
		fields = dict(request_id = 5, owner_reason = reroute_reason, owner_email = "richa@codeforamerica.org")
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