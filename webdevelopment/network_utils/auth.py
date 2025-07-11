from flask import request, jsonify, Blueprint, render_template, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from database_setup import SessionLocal, UserCredentials
from .constants import credentials

def authenticate_request(request):
    auth = request.authorization
    print("[DEBUG] auth.py loaded successfully.")
    if not auth or credentials.get(auth.username) != auth.password:
        return False
    return True

auth_bp = Blueprint('auth', __name__)

@auth_bp.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        email = request.form.get("email")
        username = request.form.get("username")
        full_name = request.form.get("full_name")
        password = request.form.get("password")

        db = SessionLocal()
        existing_user = db.query(UserCredentials).filter_by(Email=email).first()

        if existing_user:
            flash("Email already exists.", "error")
            db.close()
            return redirect(url_for("auth.signup"))

        hashed_pw = generate_password_hash(password)
        new_user = UserCredentials(
            Email=email,
            Username=username,
            FullName=full_name,
            PasswordHash=hashed_pw
        )
        db.add(new_user)
        db.commit()
        db.close()

        flash("Account created! Please log in.", "success")
        return redirect(url_for("auth.login"))

    return render_template("signup.html",hide_nav=True)

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        db = SessionLocal()
        user = db.query(UserCredentials).filter_by(Email=email).first()

        if user and check_password_hash(user.PasswordHash, password):
            session["user_id"] = user.UserID
            session["username"] = user.Username
            session.permanent = False  # 🟢 Session ends when browser/tab closes
            db.close()
            flash("Login successful!", "success")
            return redirect(url_for("index"))
        else:
            flash("Invalid email or password.", "error")
            db.close()
            return redirect(url_for("auth.login"))

    return render_template("login.html", hide_nav=True)

@auth_bp.route("/logout", methods=["GET", "POST"])
def logout():
    session.clear()
    
    if request.method == "POST":
        return "", 204  # for navigator.sendBeacon()

    flash("Logged out successfully.", "info")
    return redirect(url_for("auth.login"))
