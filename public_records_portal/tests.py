import os
from public_records_portal import app
import unittest
import random, string


class PublicRecordsTestCase(unittest.TestCase):
	def setUp(self):
	# 	app.config['TESTING'] = True
		self.app = app.test_client()
	# 	# app.init_db()

	# def tearDown(self):
	# 	# os.close(self.db_fd)
	# 	os.unlink(app.config['DATABASE'])

	def test_empty_db(self):
		page = self.app.get('/requests')
		assert 'No entries here so far' in page.data

	def test_not_empty_db(self):
		page = self.app.get('/requests')
		assert 'All requests' in page.data

	def test_submit_request(self):
		request = 'this is a new request and some random string %s' %''.join(random.choice(string.lowercase) for i in range(10))
		page = self.submit_request('richa@richa.com', request)
		assert request in page.data

	def test_submit_duplicate_request(self):
		request = 'this is a duplicate request'
		page = self.submit_request('richa@richa.com', request)
		assert 'You broke the internet' in page.data

	def submit_request(self, email, text):
		return self.app.post('/', data=dict(
		request_text= text,
		request_email = email
	), follow_redirects=True)

if __name__ == '__main__':
	unittest.main()