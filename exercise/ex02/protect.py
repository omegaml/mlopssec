import os
from flask import request, session, redirect, url_for
from .login import add_login
from .demousers import USERS
from flask_login import current_user

# Pfade, die kein Login brauchen
EXEMPT_PATHS = {'/login', '/logout', '/static'}

def is_exempt(path):
    if path in EXEMPT_PATHS:
        return True
    # einfache Prefix-Prüfung für static/ oder API-Health
    for p in EXEMPT_PATHS:
        if path.startswith(p):
            return True
    return False

def protect_all_routes(app):
    @app.before_request
    def require_login():
        if is_exempt(request.path):
            return
        # Beispiel: Session-Token entweder in Flask-Session oder Cookie prüfen
        if current_user.is_authenticated:
            return None
        if request.cookies.get('session_id'):
            # optional: validiere Token hier 
            return
        # sonst redirect auf login (mit next param)
        return redirect(url_for('auth.login', next=request.path))

    # is this secure?
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', '00309c8e727ca5d601433abad266a049')
    add_login(app, USERS)