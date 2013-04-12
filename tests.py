import os
from application import app
import unittest

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

if __name__ == '__main__':
	unittest.main()