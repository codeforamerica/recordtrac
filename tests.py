import os
from public_records_portal.prflask import app
import unittest
import random, string


class PublicRecordsTestCase(unittest.TestCase):

	def login(self, username, password):
		return self.app.post('/login', data=dict(
        email=username,
        password=password
    ), follow_redirects=True)

	def setUp(self):
		self.app = app.test_client()

	def test_empty_db(self):
		page = self.app.get('/requests')
		assert 'No entries here so far' in page.data

	def test_not_empty_db(self):
		page = self.app.get('/requests')
		assert 'All requests' in page.data

	def test_submit_request(self):
		page, request = self.make_random_request()
		assert request in page.data

	def test_home(self):
		page = self.app.get('/')
		print page
		assert 'Submit a Request' in page.data

	def make_random_request(self):
		request = 'this is a new request and some random string %s' %''.join(random.choice(string.lowercase) for i in range(10))
		return self.submit_request('richa@richa.com', request), request

	def test_question(self):
		self.login('richa@codeforamerica.org', app.config['ADMIN_PASSWORD'])
		question = 'this is a test question'
		fields = dict(request_id = 33, user_id = 2, question_text = question)
		page = self.submit_generic(fields = fields, endpoint = "add_a_qa")
		assert 'richa@codeforamerica.org' in page.data

	def test_submit_duplicate_request(self):
		request = 'this is a duplicate request'
		page = self.submit_request('richa@richa.com', request)
		assert 'You broke the internet' in page.data

	def submit_request(self, email, text):
		return self.app.post('/new', data=dict(
		request_text= text,
		request_email = email
	), follow_redirects=True)

	def submit_generic(self, fields, endpoint = ""):
		return self.app.post('/%s' % (endpoint), data = fields, follow_redirects= True)

if __name__ == '__main__':
	unittest.main()