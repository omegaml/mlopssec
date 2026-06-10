# Pfade, die kein Login brauchen
EXEMPT_PATHS = {'/login', '/signup', '/static'}

def is_exempt(path):
    if path in EXEMPT_PATHS:
        return True
    # einfache Prefix-Prüfung für static/ oder API-Health
    for p in EXEMPT_PATHS:
        if path.startswith(p):
            return True
    return False

def protect(app):
    @app.before_request
    def require_login():
        if is_exempt(request.path):
            return
        # Beispiel: Session-Token entweder in Flask-Session oder Cookie prüfen
        if 'user_id' in session:
            return  # eingeloggt
        if request.cookies.get('session_id'):
            # optional: validiere Token hier (DB/Redis)
            return
        # sonst redirect auf login (mit next param)
        return redirect(url_for('login', next=request.path))