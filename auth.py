from flask import Blueprint, render_template, redirect, url_for, request, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required
from sqlalchemy import exc

from models import User, db

auth = Blueprint("auth", __name__)


@auth.route("/login")
def login():
    return render_template("login.html", current_page="login")


@auth.route("/signup")
def signup():
    return render_template("signup.html", current_page="sign_up")


@auth.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("main.index"))


@auth.route("/signup", methods=["POST"])
def signup_post():
    first_name = request.form.get("first_name").strip().capitalize()
    last_name = request.form.get("last_name").strip().capitalize()
    username = request.form.get("username").strip()
    password = request.form.get("password").strip()

    # Check if user exists
    user = User.query.filter_by(username=username).first()
    if user:
        flash("Email address already exists")
        return redirect(url_for("auth.signup"))

    # Creates new user
    new_user = User(
        first_name=first_name,
        last_name=last_name,
        username=username,
        password=generate_password_hash(password, method="sha256"),
    )

    # Add user to db
    db.session.add(new_user)
    try:
        db.session.commit()
    except exc.SQLAlchemyError:
        flash("An error occured during user creation. Please try again.")
        return redirect(url_for("auth.signup"))

    login_user(new_user)
    return redirect(url_for("main.index"))


@auth.route("/login", methods=["POST"])
def login_post():
    username = request.form.get("username").strip()
    password = request.form.get("password").strip()
    user = User.query.filter_by(username=username).first()

    if not user or not check_password_hash(user.password, password):
        flash("Username or password incorrect. Please try again.")
        return redirect(url_for("main.index"))

    login_user(user)
    return redirect(url_for("main.index"))
