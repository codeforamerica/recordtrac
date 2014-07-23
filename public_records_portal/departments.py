import os
import json
from public_records_portal import app
from db_helpers import *
from models import Department

""" 
.. module:: prr
	:synopsis: Public records functionality as related to a municipality's different departments.
.. modlueauthor:: Richa Agarwal <richa@codeforamerica.org>
"""

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

def get_depts(user):
	depts_contact = []
	depts_backup = []
	if user.email:
		depts_json = open(os.path.join(app.root_path, 'static/json/departments.json'))
		json_data = json.load(depts_json)
		for line in json_data:
			if json_data[line]["Contact"].lower() == user.email.lower():
				depts_contact.append(line)
			if json_data[line]["Backup"].lower() == user.email.lower():
				depts_backup.append(line)
	return depts_contact, depts_backup

