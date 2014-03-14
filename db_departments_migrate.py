from public_records_portal import prr, db_helpers, departments, db, models, app
import os, random, string, json


# dir_json = open(os.path.join(app.root_path, 'static/json/directory.json'))
# json_data = json.load(dir_json)
# for line in json_data:
# 	if line['EMAIL_ADDRESS'] and line['DEPARTMENT']:
# 		email = line['EMAIL_ADDRESS'].lower()
# 		u = models.User.query.filter_by(email=email).first()
# 		d = models.Department.query.filter_by(name=line['DEPARTMENT']).first()
# 		if not d:
# 			d = models.Department(name=line['DEPARTMENT'])
# 			db.session.add(d)
# 			db.session.commit()
# 		u.department = d.id
# 		db.session.add(u)
# 		db.session.commit()


for r in models.Request.query.all():
	if type(r.point_person.user.department) is not int and not (r.point_person.user.department.isdigit()):
		u = r.point_person.user
		name = u.department
		d = models.Department.query.filter_by(name=name).first()
		if not d:
			d = models.Department(name=name)
			db.session.add(d)
			db.session.commit()
		u.department = d.id
		db.session.add(u)
		db.session.commit()
	r.department_id = r.point_person.user.department
	db.session.add(r)
	db.session.commit()

