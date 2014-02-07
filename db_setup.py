from public_records_portal import app, models, db_helpers

models.db.create_all()
db_helpers.create_viz_data()