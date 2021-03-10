from datetime import datetime, time

from app import app, db, scheduler
import json
import uuid
import string
import random
from flask import render_template, request, url_for, redirect, abort, jsonify, flash
from sqlalchemy import func
from flask_login import current_user, login_user, login_required, logout_user
from app.models import Type, User, Election, Status, Candidate, Vote
from app.forms import ElectionForm, VotePasswordForm, VotingForm

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


@app.route("/create-election", methods=['GET', 'POST'])
@login_required
def create_election():
    # if user is authenticated, make the owner of the election the current logged in user
    # if the user is not authenticated, redirect the user to the login page

    form = ElectionForm()
    if form.validate_on_submit():
        # is this necessary
        print(form.errors)
        if request.method == 'POST':
            pending_status = Status.query.get(1)
            random_link = uuid.uuid4()
            slug = ''.join(random.choices(string.ascii_uppercase + 
                            string.ascii_lowercase + string.punctuation + 
                            string.digits, k = 10)) 

            election = Election(owner=current_user, slug=slug, name=form.name.data,
                                starting_at=form.starting_at.data,
                                ending_at=form.ending_at.data,
                                description=form.description.data,
                                status=pending_status, number_of_voters=form.number_of_voters.data, link=str(
                                    random_link),
                                password=form.password.data)
            db.session.add(election)
            
            # create candidates
            for c in form.candidates.data:
                candidate = Candidate(election=election,
                                      name=c['name'], bio=c['bio'])

                db.session.add(candidate)

            db.session.commit()

            # the scheduler
            try:
                # schedule them to run the schuled_job method at their starting datetime
                # notice the change to the id as you requested
                scheduler.add_job(id="start "+election.name, func=schedule_job, trigger='date', run_date=election.starting_at, args=[election.id])    
                print("start ", election.name, election.id, " done")
                # schedule the jobs to run the schuled_job method at their ending datetime
                # notice the change to the id as you requested
                scheduler.add_job(id="end "+election.name, func=schedule_job, trigger='date', run_date=election.ending_at, args=[election.id])
                print("end ", election.name, election.id, " done")
            except Exception as e:
                print(str(e))

            flash(f'Candidates and election created succesfully', 'success')
        return redirect(url_for('election', link=random_link))
    return render_template("election_form.html", title="Create Election", form=form, count_candidates=2)


@app.route("/election/<link>", methods=['GET', 'POST'])
def election(link):
    election = Election.query.filter_by(link=link).first()
    if election is None:
        flash(f'There is no such election', 'danger')
        return redirect(url_for('missing_route'))
      
    statuses = Status.query.all()
    return render_template('election.html', title=election.name, election=election, statuses=statuses)


@app.route("/election/<link>/delete")
def delete_election(link):
    election = Election.query.filter_by(link=link).first()
    if election is None:
        flash(f'There is no such election', 'danger')
        return redirect(url_for('missing_route'))
    if election.owner.id != current_user.id:
        flash(f'Your not the owner of the election', 'danger')
        return redirect(url_for('index'))

    for c in election.candidates.all():
        db.session.delete(c)
    
    votes = election.votes.all()
    if votes is not None:
        for v in votes:
            db.session.delete(v)

    db.session.delete(election)
    db.session.commit()
    flash(f'Election and candidates have been deleted', 'success')
    return redirect(url_for('dashboard'))


@app.route("/election/<link>/update", methods=['GET', 'POST'])
def update_election(link):
    election = Election.query.filter_by(link=link).first()
    if election is None:
        flash(f'There is no such election', 'danger')
        return redirect(url_for('missing_route'))
    if election.owner != current_user:
        flash(f'Your not the owner of the election', 'danger')
        return redirect(url_for('index'))
        # return abort(403) doesn't seem to work. not sure tho

    candidates_ = election.candidates.all()
    # rename the
    form = ElectionForm(candidates=candidates_)
    print(type(candidates_))
    if form.validate_on_submit():
        election.name = form.name.data
        election.starting_at = form.starting_at.data
        election.ending_at = form.ending_at.data
        election.number_of_voters = form.number_of_voters.data
        election.description = form.description.data
        election.password = form.password.data

# first check if these candidates already exist. If they do, don't create them again
        print(form.candidates.data)
        for c in form.candidates.data:
            # todo, move this to a model function
            c_ = Candidate.query.get(c['id'])

            if c_:
                c_.name = c['name']
                c_.bio = c['bio']
                db.session.add(c_)
            # else tis a new candidate
            else:
                candidate = Candidate(election=election,
                                      name=c['name'], bio=c['bio'])
                db.session.add(candidate)

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

        # TODO: render candidates too
        candidates = to_json_array(election.candidates.all())

        # fp = forms

    return render_template("election_form.html", title="Update Election", form=form, count_candidates=len(candidates), candidates=json.dumps(candidates), election=election)


@app.route("/election/<link>/change-status", methods=['POST'])
@login_required
def change_election_status(link):
    # No need for this because flask_login provides a wrapper called login_required that does the same thing as this
    # if not current_user.is_authenticated:
    #     redirect(url_for('index'))

    election = Election.query.filter_by(link=link).first_or_404()

    if election.owner != current_user:
        flash(f'Your not the owner of the election', 'danger')
        return redirect(url_for('index'))

    status_index = request.form.get('status')

    if status_index is None:
        return redirect(url_for('missing_route'))

    status = Status.query.get(status_index)

    election.status_id = status.id
    db.session.commit()

    # Add flash message here...
    flash(f'Election status has been changed to {status.name}', 'success')
    return redirect(url_for('election', link=election.link))


@app.route("/election/<link>/remove-candidate", methods=['GET', 'POST'])
@login_required
def delete_candidate(link):

    # No need for this because flask_login provides a wrapper called login_required that does the same thing as this
    # if not current_user.is_authenticated:
    #     redirect(url_for('index'))

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


@app.route("/election/<link>/vote-candidate", methods=['GET', 'POST'])
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
            if form.password.data != election.password:
                flash(f'Incorrect password', 'danger')
                return redirect(url_for('voting_pass_link', link=link))
            else:
                flash(f'Happy voting', 'success')
                slug = election.slug
                return redirect(url_for('election_vote', link=link, slug=slug))
    return render_template('voting_pass_link.html', form=form)


@app.route("/election/<link>/vote-candidate/<slug>", methods=['GET', 'POST'])
@login_required
def election_vote(link, slug):
    election = Election.query.filter_by(link=link).first()

    
    # check if the status of the election is not started; if yes redirect to error 404 could we create flash messages for errors???
    if election.status.name != "started":
        return redirect(url_for('missing_route'))
    candidates = election.candidates


    form = VotingForm()
    form.candidates.choices = [(candidate.id, candidate.name)
                               for candidate in candidates]
    if form.validate_on_submit():
        user_vote = Vote.query.\
            filter_by(election=election, user=current_user).first()
        if user_vote is not None:
            db.session.delete(user_vote)
            db.session.commit()

        #check if the total election votes is more than or equal to the number of voters; if yes redirect to vote_limit message
        if election.votes.count() >= int(election.number_of_voters):
            return redirect(url_for('vote_limit', link=link))

        voted = request.form['candidates']
        voted_candidate = Candidate.query.filter_by(id=voted).first()
        vote = Vote(user=current_user, election=election,
                    candidate=voted_candidate)
        db.session.add(vote)
        db.session.commit()
        flash(f'You have successfully voted; may the odds forever be in your favour', 'success')
        return redirect(url_for('vote_success'))
    return render_template('election_vote.html', title="Vote", form=form, candidates=candidates)


@app.route("/election/<link>/vote-candidate/<slug>/result", methods=['GET'])
def result(link, slug):
    election = Election.query.filter_by(link=link).first()
    if election.status.name != "ended":
        flash(f'The election hasnt ended yet chill bro.................or sis', 'danger')
        return redirect(url_for('missing_route'))
    return render_template('result.html', title='Result', election=election)


@app.route("/election/<link>/max-voters", methods=['GET'])
def vote_limit(link):
    election = Election.query.filter_by(link=link).first()
    return render_template('vote_limit_message.html', election=election)

@app.route("/election/success", methods=['GET'])
def vote_success():
    return render_template('vote_success_message.html')


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
