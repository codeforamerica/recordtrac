from functools import wraps
from flask.ext.login import current_user
from flask import render_template
from public_records_portal import app
from flask.ext.login import LoginManager
from db_helpers import get_user_by_id

login_manager = LoginManager()
login_manager.user_loader(get_user_by_id)
login_manager.init_app(app)

@login_manager.unauthorized_handler
def unauthorized():
    app.logger.info("\n\nuser is unauthorized.")
    return render_template("alpha.html")
