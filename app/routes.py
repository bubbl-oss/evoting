from datetime import datetime, time
from app import app, db
import json
import uuid
from flask import render_template, request, url_for, redirect, abort
from flask_login import current_user, login_user, login_required, logout_user
from app.models import Type, User, Election, Status, Candidate
from app.forms import ElectionForm


@app.route("/")
def index():
    elections = Election.query.all()  # all elections in the system
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
        type = Type.query.get(1)  # fetch the 'individual' Type by default
        user = User(email=user_email.lower(), type=type)
        db.session.add(user)
        db.session.commit()

    login_user(user, remember=True)
    return redirect(url_for('dashboard'))


@app.route("/dashboard")
@login_required
def dashboard():
    elections = current_user.elections.all()  # all user elections
    return render_template("dashboard.html", title="User Dashboard", elections=elections)


@app.route("/create-election", methods=['GET', 'POST'])
@login_required
def create_election():
    # if user is authenticated, make the owner of the election the current logged in user
    # if the user is not authenticated, redirect the user to the login page
<<<<<<< HEAD
    if current_user.is_authenticated:
        form = ElectionForm()
        if form.validate_on_submit:
            if form.password.data is not None:
                election = Election(owner=current_user.id, name_of_election=form.name_of_election.data, 
                                    date_of_election=form.date_of_election.data, 
                                    time_of_election=form.time_of_election.data,
                                    status=form.status.data, number_of_voters=form.number_of_voters.data, 
                                    password=form.password.data)
                db.session.add(election)
                db,session.commit()
            else:
                election = Election(owner=current_user.id, name_of_election=form.name_of_election.data, 
                                    date_of_election=form.date_of_election.data, 
                                    time_of_election=form.time_of_election.data,
                                    status=form.status.data, number_of_voters=form.number_of_voters.data)
                db.session.add(election)
                db,session.commit()
        return redirect(url_for('election_url'))
    else:
        return redirect(url_for('index'))
    return render_template("create_election.html", title="Create Election", form=form)


@app.route("/election/<int:election_id>")
def election(election_id):
    election = Election.query.get_or_404(election_id)
    return render_template('election.html', title=election.name_of_election, election=election)


@app.route("/election/<int:election_id>/update", methods=['GET', 'POST'])
def update_election(election_id):
    election = Election.query.get_or_404(election_id)
=======

    # form = ElectionForm()
    form = ElectionForm(request.form)
    if form.validate_on_submit():
        pending_status = Status.query.get(1)
        random_link = uuid.uuid4()

        # return 'hi'
        election = Election(owner=current_user, name=form.name.data,
                            date_of_election=datetime.combine(
                                form.date_of_election.data, time()),
                            description=form.description.data,
                            time_of_election=form.time_of_election.data,
                            status=pending_status, number_of_voters=form.number_of_voters.data, link=str(
                                random_link),
                            password=form.password.data)
        print(election)
        db.session.add(election)
        # create candidates
        for c in form.candidates.data:
            candidate = Candidate(election=election,
                                  name=c['name'], bio=c['description'])
            print(candidate)
            db.session.add(candidate)

        db.session.commit()
        return redirect(url_for('election', link=random_link))
    return render_template("election_form.html", title="Create Election", form=form)


@app.route("/election/<link>")
def election(link):
    election = Election.query.filter_by(link=link).first()
    if election is None:
        return redirect(url_for('404.html'))
    return render_template('election.html', title=election.name, election=election)


@app.route("/election/<link>/update", methods=['GET', 'POST'])
def update_election(link):
    election = Election.query.filter_by(link=link).first()
    if election is None:
        return redirect(url_for('404.html'))
>>>>>>> 72aae7a1e5e0973c55a61977d69135be2dcad0b6
    if election.owner != current_user:
        return redirect(url_for('index'))
        # return abort(403) doesn't seem to work. not sure tho
    form = ElectionForm()
    if form.validate_on_submit():
        election.name = form.name.data
        election.date_of_election = form.date_of_election.data
        election.time_of_election = form.time_of_election.data
        election.status = form.status.data
        election.number_of_voters = form.number_of_voters.data
        election.password = form.password.data
        db.session.commit()
        return redirect(url_for('election', link=link))

    elif request.method == 'GET':
        form.name.data = election.name
        form.date_of_election.data = election.date_of_election
        form.time_of_election.data = election.time_of_election
        # form.status.data = election.status TODO: find a way to add this to the election_form
        form.number_of_voters.data = election.number_of_voters
        form.password.data = election.password
        # TODO: render candidates too
    return render_template("election_form.html", title="Update Election", form=form)


@app.route("/voting-link")
def election_url():
    return render_template('election_url.html', title="Election Url")


@app.route("/logout-complete")
def logout_complete():
    # TODO: STILL TEMPORARY
    logout_user()
    return render_template("logout_complete.html", title="Logout Complete Page")
