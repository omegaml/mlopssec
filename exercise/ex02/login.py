from flask import Flask, request, redirect, url_for, render_template, Blueprint
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

def add_login(app, users):
    # adopted from https://www.geeksforgeeks.org/python/how-to-add-authentication-to-your-app-with-flask-login/
    auth_bp = Blueprint("auth", __name__, 
                        template_folder="templates", 
                        url_prefix="")
    
    login_manager = LoginManager(app)
    login_manager.login_view = "login"
    
    class User(UserMixin):
        def __init__(self, id):
            self.id = id
    
    @login_manager.user_loader
    def load_user(user_id):
        if user_id in users:
            return User(user_id)
        return None
    
    @auth_bp.route("/login", methods=["GET", "POST"])
    def login():
        if request.method == "POST":
            username = request.form.get("username", "")
            password = request.form.get("password", "")
            user = users.get(username)
            if user and check_password_hash(user["password"], password):
                login_user(User(user["id"]))
                next_page = request.args.get("next") or url_for("index")
                return redirect(next_page)
        return render_template("login.html", error="Ungültige Anmeldedaten", ), 401
        
    @auth_bp.route("/logout")
    @login_required
    def logout():
        logout_user()
        return redirect(url_for("index"))

    app.register_blueprint(auth_bp)