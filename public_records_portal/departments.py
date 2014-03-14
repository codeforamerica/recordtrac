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
### @export "create_doctypes"
def create_doctypes():
	""" # Creates a file called doctypes.json from departments.json that is used by typeahead to map document types to the department which can fulfill it. """
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

### @export "create_list_depts"
def create_list_depts():
	depts = []
	depts_json = open(os.path.join(app.root_path, 'static/json/departments.json'))
	json_data = json.load(depts_json)
	for department in json_data:
		depts.append(department)
  	with open(os.path.join(app.root_path, 'static/json/list_of_departments.json'), 'w') as outfile:
  		json.dump(depts, outfile)

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

### @export "populate_users_with_departments"
def populate_users_with_departments():
	users = get_objs("User")
	for u in users:
		dept = Department.query.filter_by(name = get_dept(u)).first()
		if not dept:
			dept = Department(name = get_dept(u))
			db.session.add(dept)
			db.session.commit()
		if dept:
			update_obj(attribute = "department", val = dept.id, obj = u)
		depts_contact, depts_backup = get_depts(u)
		if depts_contact:
			update_obj(attribute = "contact_for", val = ",".join(depts_contact), obj = u)
		if depts_backup:
			update_obj(attribute = "backup_for", val = ",".join(depts_backup), obj = u)
