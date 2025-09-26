from functools import wraps
from flask_login import current_user
from flask import abort, url_for, redirect, flash, request

def admin_required(f):

    """
    Decorator to restrict access to routes to only authenticated administrators.
    If the current user is not authenticated or not an admin, it aborts
    with a 403 Forbidden error.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            # Optionally, you could redirect to login with a message
            flash('Please log in to access this page.', 'info')
            return redirect(url_for('login', next=request.url))
        if not current_user.is_admin:
            abort(403) # Forbidden
        return f(*args, **kwargs)
    return decorated_function