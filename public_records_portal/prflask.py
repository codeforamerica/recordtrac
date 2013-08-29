from public_records_portal import app, models, db, template_renderers
from template_renderers import * # Import all the functions that render templates
from flask.ext.restless import APIManager

# Create API
manager = APIManager(app, flask_sqlalchemy_db=db)
# The endpoints created are /api/object, e.g. publicrecordsareawesome.com/api/request/
manager.create_api(models.Request, methods=['GET', 'POST', 'PUT', 'DELETE'], results_per_page=None)
manager.create_api(models.Owner, methods=['GET', 'POST', 'PUT', 'DELETE'], results_per_page = None)
manager.create_api(models.Note, methods=['GET', 'POST', 'PUT', 'DELETE'], results_per_page = None)
manager.create_api(models.Record, methods=['GET', 'POST', 'PUT', 'DELETE'], results_per_page = None)
manager.create_api(models.QA, methods=['GET', 'POST', 'PUT', 'DELETE'], results_per_page =None)
manager.create_api(models.Subscriber, methods=['GET', 'POST', 'PUT', 'DELETE'], results_per_page = None)

# Routing dictionary. 
routing = {
#   function_name: url
	'your_requests':{
		'url': '/your_requests'
	},
	'tutorial':{
		'url': '/tutorial'
	},
	'index':{
		'url':'/', 
		'methods':['GET', 'POST']
	},
	'explain_all_actions':{
		'url': '/actions'
	},
	'new_request': {
		'url': '/new', 
		'methods': ['GET', 'POST']
	},
	'show_response':{
		'url': '/response/<int:request_id>'
	},
	'edit_case':{
		'url': '/edit/request/<int:request_id>'
	},
	'show_request_for_x':{
		'url': '/<string:audience>/request/<int:request_id>'
	},
	'show_request':{
		'url': '/request/<int:request_id>'
	},
	'any_page':{
		'url': '/<page>'
	},
	'requests':{
		'url': '/requests'
	},
	'update_password':{
		'url': '/update_password', 
		'methods': ['GET', 'POST']
	},
	'logout':{
		'url': '/logout'
	},
	'login':{
		'url': '/login', 'methods': ['GET', 'POST']
	},
	'add_a_resource':{
		'url': '/add_a_<string:resource>', 
		'methods': ['GET', 'POST']
	},
	'public_add_a_resource':{
		'url': '/public_add_a_<string:resource>', 
		'methods': ['GET', 'POST']
	},
	'update_a_resource':{
		'url': '/update_a_<string:resource>', 
		'methods': ['GET', 'POST']
	},
	'close':{
		'url': '/close', 
		'methods': ['GET', 'POST']
	},
	'staff_card':{
		'url': '/staff_card/<int:user_id>'
	}
}


def route_url(function_name):
	methods = None
	if 'methods' in routing[function_name]:
		methods = routing[function_name]['methods']
	app.add_url_rule(routing[function_name]['url'], function_name, eval(function_name), methods = methods)

for function_name in routing:
	route_url(function_name)