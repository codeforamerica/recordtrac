import os
import json
from public_records_portal import app
from db_helpers import *

""" 
.. module:: prr
	:synopsis: Public records functionality as related to a municipality's different departments.
.. modlueauthor:: Richa Agarwal <richa@codeforamerica.org>
"""
### @export "create_doctypes"
# Creates a file called doctypes.json from departments.json that is used by typeahead to map document types to the department which can fulfill it
### @export "create_doctypes"
def create_doctypes():
	depts = []
	depts_json = open(os.path.join(app.root_path, 'static/json/departments.json'))
	json_data = json.load(depts_json)
	for department in json_data:
		if "Council" in department:
			document_types = ['Council records']
		else:
			document_types = json_data[department]["Document Types"]
		for document_type in document_types:
			line = {}
			line['DEPARTMENT'] = department
			line['DOC_TYPE'] = document_type
			depts.append(line)
	with open(os.path.join(app.root_path, 'static/json/doctypes.json'), 'w') as outfile:
  		json.dump(depts, outfile)

def create_viz_data():
	depts_freq = []
	depts_json = open(os.path.join(app.root_path, 'static/json/list_of_departments.json'))
	json_data = json.load(depts_json)
	for department in json_data:
		line = {}
		line['department'] = department
		line['freq'] = len(get_requests_by_filters(line))
		depts_freq.append(line)
	# Only display top 5 departments:
	depts_freq.sort(key = lambda x:x['freq'], reverse = True)
	del depts_freq[5:]
	with open(os.path.join(app.root_path, 'static/json/responses_data.json'), 'w') as outfile:
  		json.dump(depts_freq, outfile)

### @export "create_list_depts"
def create_list_depts():
	depts = []
	depts_json = open(os.path.join(app.root_path, 'static/json/departments.json'))
	json_data = json.load(depts_json)
	for department in json_data:
		depts.append(department)
  	with open(os.path.join(app.root_path, 'static/json/list_of_departments.json'), 'w') as outfile:
  		json.dump(depts, outfile)

### @export "get_prr_liaison"
def get_prr_liaison(dept):
	depts_json = open(os.path.join(app.root_path, 'static/json/departments.json'))
	json_data = json.load(depts_json)
	if dept in json_data:
		return json_data[dept]["Contact"]
	return None

### @export "get_dept_backup"
def get_dept_backup(dept_contact):
	depts_json = open(os.path.join(app.root_path, 'static/json/departments.json'))
	json_data = json.load(depts_json)
	for line in json_data:
		if json_data[line]["Contact"].lower() == dept_contact.lower():
			return json_data[line]["Backup"]
	return None

### @export "get_dept"
def get_dept(user):
	if user.email:
		depts_json = open(os.path.join(app.root_path, 'static/json/departments.json'))
		json_data = json.load(depts_json)
		for line in json_data:
			if json_data[line]["Contact"].lower() == user.email.lower():
				return line
	return None

### @export "populate_users_with_departments"
def populate_users_with_departments():
	users = get_objs("User")
	for u in users:
		dept = get_dept(u)
		if dept:
			update_obj(attribute = "department", val = dept, obj = u)








