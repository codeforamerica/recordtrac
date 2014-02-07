from public_records_portal import prr
from public_records_portal.prflask import app
import os, random, string, json

common_requests = ['City Council meeting minutes', 'Police Report', 'Incident Report', 'Communication between Councilmembers']
depts_json = open(os.path.join(app.root_path, 'static/json/list_of_departments.json'))
departments = json.load(depts_json)

# Create some seed data so our tests run
for i in range(20):
	request_type = random.choice(common_requests)
	request_department = random.choice(departments)
	random_number = random.randrange(0, 901, 4)
	request_text = "%(request_type)s %(random_number)s" % locals()
	prr.make_request(text=request_text, email = 'richa@postcode.io', alias = 'Richa', department = request_department)
