from public_records_portal import app, models, db, db_helpers, departments, prr

models.db.create_all()

# Set user data - depends on existence of staff.csv
prr.set_directory_fields()

