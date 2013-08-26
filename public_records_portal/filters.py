from public_records_portal import app, gravatar, prr, notifications, helpers, scribd_helpers, db_helpers
# Register your filter here!
app.jinja_env.filters['get_requester'] = prr.get_requester
app.jinja_env.filters['is_request_open'] = prr.is_request_open
app.jinja_env.filters['get_scribd_download_url'] = scribd_helpers.get_scribd_download_url
app.jinja_env.filters['last_note'] = prr.last_note
app.jinja_env.filters['due_date'] = notifications.due_date
app.jinja_env.filters['get_obj'] = db_helpers.get_obj
app.jinja_env.filters['date_granular'] = helpers.date_granular
app.jinja_env.filters['get_attribute'] = db_helpers.get_attribute
app.jinja_env.filters['get_responses_chronologically'] = prr.get_responses_chronologically
app.jinja_env.filters['get_request_data_chronologically'] = prr.get_request_data_chronologically
app.jinja_env.filters['get_subscriber_attribute'] = prr.get_subscriber_attribute
app.jinja_env.filters['get_gravatar_url'] = gravatar.get_gravatar_url
app.jinja_env.filters['date'] = helpers.date
app.jinja_env.filters['explain_action'] = helpers.explain_action
app.jinja_env.filters['tutorial'] = helpers.tutorial
app.jinja_env.filters['directory'] = helpers.directory
app.jinja_env.filters['new_lines'] = helpers.new_lines
