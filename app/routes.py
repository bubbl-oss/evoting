from datetime import datetime, time
from app import app, db
import json
import uuid
from flask import render_template, request, url_for, redirect, abort
from flask_login import current_user, login_user, login_required, logout_user
from app.models import Type, User, Election, Status, Candidate, Vote
from app.forms import ElectionForm, VotePasswordForm, VotingForm
from sqlalchemy import and_


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
    if election.owner != current_user:
        return redirect(url_for('index'))
        # return abort(403) doesn't seem to work. not sure tho
    form = ElectionForm()
    if form.validate_on_submit():
        election.name = form.name.data
        election.date_of_election = form.date_of_election.data
        election.time_of_election = form.time_of_election.data
        # election.status = form.status.data
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


@app.route("/election/<link>/vote", methods=['GET','POST'])
@login_required
def voting_pass_link(link):
    election = Election.query.filter_by(link=link).first()
    if election is None:
        return redirect(url_for('404.html'))
    password = election.password

    form = VotePasswordForm()
    if form.validate_on_submit():
        if password is not None:
            if form.password.data != password:
                return redirect(url_for('voting_pass_link', link=link))
            else:
                return redirect(url_for('election_vote', link=link))
    return render_template('voting_pass_link.html', form=form) 


@app.route("/election/<link>/vote/candidate", methods=['GET', 'POST'])
@login_required
def election_vote(link):
    election = Election.query.filter_by(link=link).first()
    candidates = election.candidates


    form = VotingForm()
    form.candidates.choices = [(candidate.id, candidate.name) for candidate in candidates]
    if form.validate_on_submit():
        user_vote = Vote.query.\
            filter_by(election=election, user=current_user).first()
        if user_vote is not None:
            db.session.delete(user_vote)
            db.session.commit()

        voted = request.form['candidates']
        voted_candidate = Candidate.query.filter_by(id=voted).first()
        vote = Vote(user=current_user, election=election, candidate=voted_candidate)
        db.session.add(vote)
        db.session.commit()
        return redirect(url_for('vote_success'))
    return render_template('election_vote.html', title="Vote", form=form, candidates=candidates)

@app.route("/election/success", methods=['GET'])
def vote_success():
    return render_template('vote_success_message.html')


@app.route("/logout-complete")
def logout_complete():
    # TODO: STILL TEMPORARY
    logout_user()
    return render_template("logout_complete.html", title="Logout Complete Page")
