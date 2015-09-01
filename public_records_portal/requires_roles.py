from functools import wraps
from flask.ext.login import current_user
from unauthorized_handler import unauthorized

def requires_roles(*roles):
    def wrapper(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if current_user.role not in roles:
                return unauthorized()
            return f(*args, **kwargs)
        return wrapped
    return wrapper

