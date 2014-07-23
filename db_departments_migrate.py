from public_records_portal import prr, db_helpers, departments, db, models, app
import os, random, string, json


# First, update the users with departments in directory.json
dir_json = open(os.path.join(app.root_path, 'static/json/directory.json'))
json_data = json.load(dir_json)
for line in json_data:
	if line['EMAIL_ADDRESS'] and line['DEPARTMENT']:
		email = line['EMAIL_ADDRESS'].lower()
		u = models.User.query.filter_by(email=email).first()
		if u:
			d = models.Department.query.filter_by(name=line['DEPARTMENT']).first()
			if not d:
				d = models.Department(name=line['DEPARTMENT'])
				db.session.add(d)
				db.session.commit()
			u.department = d.id
			db.session.add(u)
			db.session.commit()


# Then, make sure PRR Liaisons get set with departments in departments.json
departments.populate_users_with_departments()


# Then, update all requests with this department data
for r in models.Request.query.all():
	# is_point_person is now used on Owner to indicate if they are the 'current owner', and current_owner on a Request is now deprecated, so make sure this gets updated:
	try:
		owner_id = r.current_owner
		o = models.Owner.query.get(owner_id)
		o.is_point_person = True
		db.session.add(o)
		db.session.commit()
	except:
		pass
	point_person = r.point_person()
	if point_person and point_person.user and point_person.user.department:
		if type(point_person.user.department) is not int and not (point_person.user.department.isdigit()):
			u = point_person.user
			name = u.department
			d = models.Department.query.filter_by(name=name).first()
			if not d:
				d = models.Department(name=name)
				db.session.add(d)
				db.session.commit()
			u.department = d.id
			db.session.add(u)
			db.session.commit()
		r.department_id = point_person.user.department
		db.session.add(r)
		db.session.commit()







