from public_records_portal import app, models, db, db_helpers, departments

models.db.create_all()
departments.create_list_depts()
db_helpers.create_viz_data()
if app.config['DEFAULT_OWNER_EMAIL'] and app.config['DEFAULT_OWNER_NAME']:
	user = models.User(email = app.config['DEFAULT_OWNER_EMAIL'], alias = app.config['DEFAULT_OWNER_NAME'], password = app.config['ADMIN_PASSWORD'])
	db.session.add(user)
	db.session.commit()