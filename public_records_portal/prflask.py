"""
    public_records_portal.prflask
    ~~~~~~~~~~~~~~~~

    Sets up API and admin endpoints for the RecordTrac flask application.

"""



from public_records_portal import app, models, db, views
from views import * # Import all the functions that render templates
from flask.ext.restless import APIManager

# Create API
manager = APIManager(app, flask_sqlalchemy_db=db)


# The endpoints created are /api/object, e.g. publicrecordsareawesome.com/api/request/
manager.create_api(models.Request, methods=['GET'], results_per_page = 10, allow_functions = True, include_columns=['date_created', 'date_received', 'department', 'id', 'notes', 'offline_submission_type', 'owners', 'qas', 'records', 'status', 'status_updated', 'text'])
# manager.create_api(models.Owner, methods=['GET'], results_per_page = 10, allow_functions = True)
manager.create_api(models.Note, methods=['GET'], results_per_page = 10, allow_functions = True)
manager.create_api(models.Record, methods=['GET'], results_per_page = 10, allow_functions = True)
manager.create_api(models.QA, methods=['GET'], results_per_page =10, allow_functions = True)
# manager.create_api(models.Subscriber, methods=['GET'], results_per_page = 10, allow_functions = True)
manager.create_api(models.Visualization, methods=['GET'], results_per_page = 10, allow_functions = True)
