from functools import wraps

from flask import flash, redirect, url_for
from flask_login import current_user
from BlogApp.models import Auth


def check_confirmed(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        user = Auth.query.filter_by(email=current_user.email).first_or_404()
        if user.confirmed is False:
            flash('Please confirm your account!', 'warning')
            return redirect('/unconfirmed')
        return func(*args, **kwargs)

    return decorated_function