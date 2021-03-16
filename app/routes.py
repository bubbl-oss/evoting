from flask.helpers import make_response
from app.tools import calculate_election_result
from datetime import datetime, time

from app import app, db, scheduler
import json
import uuid
import string
import random
from flask import render_template, request, url_for, redirect, abort, jsonify, flash
from sqlalchemy import func
from flask_login import current_user, login_user, login_required, logout_user
from app.models import Position, Type, User, Election, Status, Candidate, Vote, Result
from app.forms import CandidateForm, ElectionForm, PositionForm, VotePasswordForm, VotingForm

# I WILL ADD COMMENTS LATER


def to_json_array(collection):
    list = []
    for item in collection:
        list.append(item.as_dict())
    return list


@app.route("/")
def index():
    # get all elections that have this status. pending
    status = Status.query.get(1)
    elections = Election.query.with_parent(
        status).all()  # all elections in the system
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
    flash(f'Login success', 'success')
    return redirect(url_for('dashboard'))


@app.route("/dashboard")
@login_required
def dashboard():
    elections = current_user.elections.all()  # all user elections
    return render_template("dashboard.html", title="User Dashboard", elections=elections)


@app.route("/elections/new", methods=['GET', 'POST'])
@login_required
def new_election():

    form = ElectionForm()
    if form.validate_on_submit():
        # is this necessary
        print(form.errors)
        if request.method == 'POST':
            pending_status = Status.query.get(1)
            random_link = uuid.uuid4()

            election = Election(owner=current_user, name=form.name.data,
                                starting_at=form.starting_at.data,
                                ending_at=form.ending_at.data,
                                description=form.description.data,
                                status=pending_status, number_of_voters=form.number_of_voters.data, link=str(
                                    random_link),
                                password=str(form.password.data).lower())
            db.session.add(election)

            db.session.commit()

            # the scheduler
            try:
                # schedule them to run the schuled_job method at their starting datetime
                # notice the change to the id as you requested
                scheduler.add_job(id="start " + election.name, func=schedule_job,
                                  trigger='date', run_date=election.starting_at, args=[election.id])
                # schedule the jobs to run the schuled_job method at their ending datetime
                # notice the change to the id as you requested
                scheduler.add_job(id="end " + election.name, func=schedule_job,
                                  trigger='date', run_date=election.ending_at, args=[election.id])
            except Exception as e:
                print(str(e))

            flash(f'Election created succesfully', 'success')
        return redirect(url_for('election', link=random_link))
    return render_template("elections/form.html", title="New Election", form=form, count_candidates=2)


@app.route("/elections/<link>", methods=['GET', 'POST'])
def election(link):
    election = Election.query.filter_by(link=link).first()

    position = Position.query.filter_by(election=election).first()

    if election is None:
        flash(f'There is no such election', 'danger')
        return redirect(url_for('missing_route'))

    statuses = Status.query.all()
    return render_template('elections/index.html', title=election.name, election=election, statuses=statuses, position=position)


@app.route("/elections/<link>/update", methods=['GET', 'POST'])
def update_election(link):
    election = Election.query.filter_by(link=link).first()
    if election is None:
        flash(f'There is no such election', 'danger')
        return redirect(url_for('missing_route'))
    if election.owner != current_user:
        flash(f'Your not the owner of the election', 'danger')
        return redirect(url_for('index'))
        # return abort(403) doesn't seem to work. not sure tho

    form = ElectionForm()
    if form.validate_on_submit() and request.method == 'POST':
        election.name = form.name.data
        election.starting_at = form.starting_at.data
        election.ending_at = form.ending_at.data
        election.number_of_voters = form.number_of_voters.data
        election.description = form.description.data
        election.password = str(form.password.data).lower()

        db.session.commit()

        flash(f'Election has been updated succesfully', 'success')

        return redirect(url_for('election', link=link))

    elif request.method == 'GET':
        form.name.data = election.name
        form.starting_at.data = election.starting_at
        form.ending_at.data = election.ending_at
        form.description.data = election.description
        form.number_of_voters.data = election.number_of_voters
        form.password.data = election.password

    return render_template("elections/form.html", title="Update Election", form=form, election=election)


@app.route("/elections/<link>/delete")
def delete_election(link):
    election = Election.query.filter_by(link=link).first()

    if election is None:
        flash(f'There is no such election', 'danger')
        return redirect(url_for('missing_route'))
    if election.owner.id != current_user.id:
        flash(f'Your not the owner of the election', 'danger')
        return redirect(url_for('index'))

    election_positions = election.positions.all()

    for p in election_positions:
        db.session.delete(p)

    for p in election_positions:
        if p.candidates is not None:
            for c in p.candidates:
                db.session.delete(c)

    for p in election_positions:
        if p.votes is not None:
            for v in p.votes:
                db.session.delete(v)

    db.session.delete(election)
    db.session.commit()
    flash(f'Election and candidates have been deleted', 'success')
    return redirect(url_for('index'))


@app.route("/elections/<link>/change-status", methods=['POST'])
@login_required
def change_election_status(link):

    election = Election.query.filter_by(link=link).first_or_404()

    if election.owner != current_user:
        flash(f'You\'re not the owner of the election', 'danger')
        return redirect(url_for('index'))

    status_index = request.form.get('status')

    if status_index is None:
        return redirect(url_for('missing_route'))

    status = Status.query.get(status_index)

    election.status_id = status.id

    db.session.commit()

    flash(f'Election status has been changed to {status.name}', 'success')
    return redirect(url_for('election', link=election.link))


@app.route("/elections/<link>/positions/new", methods=['GET', 'POST'])
def new_position(link):
    election = Election.query.filter_by(link=link).first()
    if election is None:
        flash(f'There is no such election', 'danger')
        return redirect(url_for('missing_route'))

    form = PositionForm()
    if form.validate_on_submit():
        position = Position(
            title=form.title.data, description=form.description.data, election_id=election.id)
        try:
            db.session.add(position)
            db.session.commit()
            flash(f'Position added to Election', 'success')
        except:
            db.session.rollback()
            flash(f'Error creating Position', 'success')
        return redirect(url_for('election', link=link))

    return render_template('positions/form.html', title=f'New {election.name} Position', form=form, election=election)


@app.route("/elections/<link>/positions/<position_id>", methods=['GET', 'POST'])
def position(link, position_id):

    election = Election.query.filter_by(link=link).first()

    if election is None:
        flash(f'There is no such election', 'danger')
        return redirect(url_for('missing_route'))

    position = Position.query.filter_by(
        election=election, id=position_id).first()

    if position is None:
        flash(f'There is no such position', 'danger')
        return redirect(url_for('missing_route'))

    return render_template('positions/index.html', title=f"{position.title} | {election.name}", election=election, position=position)


@app.route("/elections/<link>/positions/<position_id>/update", methods=['GET', 'POST'])
def update_position(link, position_id):
    # TODO: add a guard to prevent unauthorized access!

    position = Position.query.get(position_id)

    if position is None:
        flash(f'There is no such position', 'danger')
        return redirect(url_for('missing_route'))

    form = PositionForm()
    if form.validate_on_submit() and request.method == 'POST':
        position.title = form.title.data
        position.description = form.description.data
        try:
            db.session.commit()
        except:
            db.session.rollback()
        flash(f'Position updated successfully!', 'success')
        return redirect(url_for('election', link=link))
    elif request.method == 'GET':

        form.title.data = position.title
        form.description.data = position.description

        return render_template('positions/form.html', title=f'Update {position.title} position', form=form, position=position)


@app.route("/elections/<link>/positions/<position_id>/delete", methods=['GET'])
def delete_position(link, position_id):
    position = Position.query.get_or_404(position_id)
    election = Election.query.filter_by(link=link).first()
    if election is None:
        flash(f'There is no such election', 'danger')
        return redirect(url_for('missing_route'))
    if election.owner.id != current_user.id:
        flash(f'Your not the owner of the election', 'danger')
        return redirect(url_for('index'))

    election_candidates = position.candidates.all()

    if election_candidates is not None:
        for c in election_candidates:
            db.session.delete(c)

    position_votes = position.votes.all()

    if position_votes is not None:
        for p_votes in position_votes:
            db.session.delete(p_votes)

    db.session.delete(position)
    db.session.commit()
    flash(f'Position has been deleted', 'success')
    return redirect(url_for('election', link=link))


@app.route("/elections/<link>/positions/<position_id>/candidates/new", methods=['GET', 'POST'])
def new_candidate(link, position_id):
    # TODO: add a guard to prevent unauthorized access!

    position = Position.query.get(position_id)

    if position is None:
        flash(f'There is no such position', 'danger')
        return redirect(url_for('missing_route'))

    form = CandidateForm()
    if form.validate_on_submit():
        candidate = Candidate(name=form.name.data,
                              bio=form.bio.data, position_id=position.id)
        try:
            db.session.add(candidate)
            db.session.commit()
        except:
            db.session.rollback()
        flash(f'Candidate added to position', 'success')
        return redirect(url_for('election', link=link))

    return render_template('candidates/form.html', title=f'New Candidate for {position.title}', form=form)


@app.route("/elections/<link>/positions/<position_id>/candidates/<candidate_id>", methods=['GET', 'POST'])
def candidate(link, position_id, candidate_id):

    position = Position.query.get(position_id)

    if position is None:
        flash(f'There is no such position', 'danger')
        return redirect(url_for('missing_route'))

    # TODO: check if you can query the Candidate from Position directly
    candidate = Candidate.query.filter_by(
        position=position, id=candidate_id).first()

    if candidate is None:
        flash(f'There is no such candidate', 'danger')
        return redirect(url_for('missing_route'))

    return render_template('candidates/index.html', title=f"{candidate.name} | {position.title} in {position.election.name}", candidate=candidate, position=position)


@app.route("/elections/<link>/positions/<position_id>/candidates/<candidate_id>/update", methods=['GET', 'POST'])
def update_candidate(link, position_id, candidate_id):
    # TODO: add a guard to prevent unauthorized access!

    candidate = Candidate.query.get(candidate_id)

    if candidate is None:
        flash(f'There is no such candidate', 'danger')
        return redirect(url_for('missing_route'))

    form = CandidateForm()
    if form.validate_on_submit() and request.method == 'POST':
        candidate.name = form.name.data
        candidate.bio = form.bio.data
        try:
            db.session.commit()
        except:
            db.session.rollback()
        flash(f'Candidate updated successfully!', 'success')
        return redirect(url_for('election', link=link))
    elif request.method == 'GET':

        form.name.data = candidate.name
        form.bio.data = candidate.bio
        return render_template('candidates/form.html', title=f'Update Candidate {candidate.name}', form=form)


@app.route("/elections/<link>/positions/<position_id>/candidates/<candidate_id>/delete", methods=['GET'])
def delete_candidate(link, position_id, candidate_id):
    candidate = Candidate.query.get_or_404(candidate_id)
    election = Election.query.filter_by(link=link).first()
    if election is None:
        flash(f'There is no such election', 'danger')
        return redirect(url_for('missing_route'))
    if election.owner.id != current_user.id:
        flash(f'Your not the owner of the election', 'danger')
        return redirect(url_for('index'))

    candidate_votes = candidate.votes.all()

    if candidate_votes is not None:
        for c_votes in candidate_votes:
            db.session.delete(c_votes)

    db.session.delete(candidate)
    db.session.commit()
    flash(f'Candidate has been deleted', 'success')
    return redirect(url_for('election', link=link))

# DEPRECATED


@app.route("/elections/<link>/remove-candidate", methods=['GET', 'POST'])
@login_required
def delete_candidate_http(link):

    election = Election.query.filter_by(link=link).first_or_404()

    if election.owner != current_user:
        flash(f'Your not the owner of the election', 'danger')
        return redirect(url_for('index'))

    index = int(request.args.get('i') if request.args.get(
        'i') and request.args.get('i').isdigit() else -1)

    print(index)

    candidate = Candidate.query.get(index)

    if candidate and candidate.election == election:
        # delete!
        db.session.delete(candidate)
        db.session.commit()
        flash(f'Candidate has been deleted', 'success')
        all_c = election.candidates.all()

        form = ElectionForm(candidates=all_c)

        return render_template("partials/_candidates_list.html", form=form)

    return redirect(url_for('missing_route'))


@app.route("/elections/<link>/vote/pass", methods=['GET', 'POST'])
@login_required
def voting_pass_link(link):
    election = Election.query.filter_by(link=link).first()
    # check if the status of the election is not started; if yes redirect to error 404 could we create flash messages for errors???
    if election.status.name != "started":
        flash(f'The election hasnt started yet chill bro.................or sis', 'danger')
        return redirect(url_for('missing_route'))

    if election is None:
        flash(f'There is no such election', 'danger')
        return redirect(url_for('missing_route'))

    form = VotePasswordForm()
    if form.validate_on_submit():
        if election.password is not None:
            if form.password.data == election.password:
                flash(f'Happy voting', 'success')
                # add voting cookie with value of election id and expiration at the election
                # ending time...
                res = make_response(
                    redirect(url_for('election_vote', link=link)))
                res.set_cookie('evoting-user-can-vote',
                               str(election.id), expires=int(datetime.timestamp(election.ending_at)))

                return res
            else:
                flash(f'Incorrect password', 'danger')
                return redirect(url_for('voting_pass_link', link=link))
    return render_template('voting_pass_link.html', form=form)


@app.route("/elections/<link>/vote/cast", methods=['GET', 'POST'])
@login_required
def election_vote(link):
    election = Election.query.filter_by(link=link).first()

    cookie = request.cookies.get('evoting-user-can-vote')
    if cookie is None:
        # user is not authenticated for this election and needs to enter password
        flash(f'Login to Election to vote', 'error')
        return redirect(url_for('voting_pass_link', link=link))

    # check if the status of the election is not started; if yes redirect to error 404 could we create flash messages for errors???
    if election.status.name != "started":
        return redirect(url_for('missing_route'))

    positions = Position.query.filter_by(election=election).all()

    form = VotingForm()

    if request.method == 'POST':
        for position in positions:
            user_vote = Vote.query.\
                filter_by(position=position, user=current_user).first()
            if user_vote is not None:
                db.session.delete(user_vote)
                db.session.commit()

        # check if the total election votes is more than or equal to the number of voters; 
        # if yes redirect to vote_limit message
        for p in election.positions.all():
            if p.votes.count() >= int(election.number_of_voters):
                return redirect(url_for('vote_limit', link=link))

        for position in positions:
            voted = request.form[str(position.title)]
            voted_candidate = Candidate.query.filter_by(id=voted).first()
            vote = Vote(user=current_user, position=position,
                        candidate=voted_candidate)
        
            print(vote)
            db.session.add(vote)
        db.session.commit()
        flash(f'You have successfully voted; may the odds forever be in your favour', 'success')
        # delete cookie for this election...
        res = make_response(redirect(url_for('vote_success')))
        res.set_cookie('evoting-user-can-vote', '', expires=0)
        return res
    return render_template('elections/election_vote.html', title="Vote", form=form, positions=positions, election=election)


@app.route("/elections/<link>/vote/result", methods=['GET'])
def result(link):
    return redirect(url_for('election', link=link) + '#results')


@app.route("/elections/<link>/max-voters", methods=['GET'])
def vote_limit(link):
    election = Election.query.filter_by(link=link).first()
    return render_template('vote_limit_message.html', election=election)


@app.route("/elections/success", methods=['GET'])
def vote_success():
    return render_template('vote_success_message.html')

# NOT USED


@app.route("/statuses")
def get_statuses():
    cs = Election.query.get(1)
    return jsonify(cs.as_dict())


@app.route("/logout-complete")
def logout_complete():
    # TODO: STILL TEMPORARY
    logout_user()
    flash(f'You have logged out succesfully', 'success')
    return render_template("logout_complete.html", title="Logout Complete Page")


# DEPRECATED
@app.route("/add-candidate", methods=["GET", "POST"])
def add_candidate():

    candidates_list = []

    # if the query says 1 extra candidate, we add it!
    # original_form = ElectionForm(request.form)
    # candidates_list = original_form.candidates.data

    number_of_candidates = int(request.args.get('c') if request.args.get(
        'c') and request.args.get('c').isdigit() else 0)
    if number_of_candidates > 0:
        for c in range(int(number_of_candidates) + 1):
            # add the extra fields now...
            candidates_list.append({"name": "", "bio": ""})

    print(request.args.get('c'))
    print(candidates_list)

    form = ElectionForm(candidates=candidates_list)
    new_field = form.candidates[-1]
    new_field.name = ""
    new_field.bio = ""
    return render_template("partials/candidate_input.html", c=new_field)


# DEPRECATED
@app.route("/remove-candidate", methods=["GET", "POST"])
def remove_candidate():

    form = ElectionForm(request.form)

    return render_template("partials/_candidates_list.html", form=form)


@app.route("/404", methods=["GET"])
def missing_route():
    return render_template("404.html")


def schedule_job(id):
    election = Election.query.get(id)
    # if election status is pending set to started
    if election.status_id == 1:
        election.status_id = 2
    # if election status is started set to ended
    elif election.status_id == 2:
        election.status_id = 3
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
