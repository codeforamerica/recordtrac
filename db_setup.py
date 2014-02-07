from public_records_portal import app, models, db_helpers, departments

models.db.create_all()
departments.create_list_depts()
db_helpers.create_viz_data()