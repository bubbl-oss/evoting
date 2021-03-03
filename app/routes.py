from app import app, db
from flask import render_template, request, url_for, redirect
from flask_login import login_user, login_required, logout_user
from app.models import User


@app.route("/")
def index():
    elections = [
        {"id": 1, "name_of_election": "SGA 2021", "status": "Not Started"},
        {"id": 2, "name_of_election": "MSS Spring Leadership", "status": "Not Started"},
        {"id": 3, "name_of_election": "Honor Society", "status": "Not Started"},
        {"id": 4, "name_of_election": "Finest Boy", "status": "Not Started"}

    ]
    return render_template("index.html", title="Home Page", elections=elections)


@app.route("/login-complete")
def login_complete():
    # bubbl_user_cookie = request.cookies.get('bubbl-user')
    # <<< TODO: THIS IS SO TEMPORARY, I WILL MAKE IT MORE SECURE LATER >>>
    # token should be sent by auth service and should only be able to work once.
    bubbl_user_token = request.args.get('token')

    # if the bubbl_user cookie does not exist!
    if not bubbl_user_token:
        return redirect(url_for("index"))

    user_email = request.args.get('user')
    user = User.query.filter_by(email=user_email.lower()).first()
    # if the user already exists... just log them in
    # but if the user does not exist at all, create new user
    if user is None:
        user = User(email=user_email.lower())
        db.session.add(user)
        db.session.commit()

    login_user(user, remember=True)
    return redirect(url_for('dashboard'))


@app.route("/dashboard")
@login_required
def dashboard():
    elections = [
        {"id": 1, "name_of_election": "SGA 2021", "status": "Not Started"},
        {"id": 2, "name_of_election": "MSS Spring Leadership", "status": "Not Started"},
        {"id": 3, "name_of_election": "Honor Society", "status": "Not Started"},
        {"id": 4, "name_of_election": "Finest Boy", "status": "Not Started"}

    ]
    return render_template("dashboard.html", title="User Dashboard", elections=elections)


@app.route("/create-election")
def create_election():
    return render_template("create_election.html", title="Create Election")


@app.route("/logout-complete")
def logout_complete():
    # TODO: STILL TEMPORARY
    logout_user()
    return render_template("logout_complete.html", title="Logout Complete Page")
