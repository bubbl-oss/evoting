from app import db, login
from flask_login import UserMixin
from datetime import datetime
from sqlalchemy import event
from app.tools import calculate_election_result
from app.constants import eStatus


class Type(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String())
    user = db.relationship('User', backref='type', lazy='dynamic')

    def __repr__(self):
        return f'<Type {self.name}>'

    def as_dict(self):
        return {item.name: getattr(self, item.name) for item in self.__table__.columns}


class User(UserMixin, db.Model):

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    type_id = db.Column(db.Integer, db.ForeignKey('type.id'), nullable=False)
    verified = db.Column(db.Boolean)
    elections = db.relationship('Election', backref='owner', lazy='dynamic')
    votes = db.relationship('Vote', backref='user', lazy='dynamic')

    def __repr__(self):
        return f'<User {self.email}>'

    def as_dict(self):
        return {item.name: getattr(self, item.name) for item in self.__table__.columns}

    def get_name(self):
        """Splits 'firstname.lastname@aun.edu.ng' into a list ['firstname', 'lastname']
        if it's only one name, the list only contains one element ['firstname']
        """
        name = self.email[:self.email.find('@')]

        return name.split('.')


class Status(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable=False)
    election = db.relationship('Election', backref='status', lazy='dynamic')

    def __repr__(self):
        return f'<Status {self.name}>'

    def as_dict(self):
        return {item.name: getattr(self, item.name) for item in self.__table__.columns}


class Election(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable=False, index=True)
    description = db.Column(db.String())
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    modified_at = db.Column(db.DateTime, default=datetime.utcnow)
    starting_at = db.Column(db.DateTime, index=True)
    ending_at = db.Column(db.DateTime)
    link = db.Column(db.String())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    status_id = db.Column(db.Integer, db.ForeignKey(
        'status.id'), nullable=False)
    positions = db.relationship(
        'Position', backref='election', lazy='dynamic',
        passive_deletes=True, cascade="all, delete")
    number_of_voters = db.Column(db.String(), nullable=False)
    password = db.Column(db.String())

    def __repr__(self):
        return f'<Election {self.name}>'

    def as_dict(self):
        return {item.name: getattr(self, item.name) for item in self.__table__.columns}


class Position(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(), nullable=False, index=True)
    description = db.Column(db.String())
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    modified_at = db.Column(db.DateTime, default=datetime.utcnow)
    election_id = db.Column(db.Integer, db.ForeignKey(
        'election.id', ondelete='CASCADE'), nullable=False)
    candidates = db.relationship(
        'Candidate', backref='position', lazy='dynamic',
        passive_deletes=True, cascade="all, delete")
    votes = db.relationship('Vote', backref='position', lazy='dynamic',
                            passive_deletes=True, cascade="all, delete")
    results = db.relationship('Result', backref='position', lazy='dynamic',
                              passive_deletes=True, cascade="all, delete")

    def __repr__(self):
        return f'<Position {self.title} {self.election}>'

    def as_dict(self):
        return {item.name: getattr(self, item.name) for item in self.__table__.columns}


class Candidate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable=False, index=True)
    image = db.Column(db.String())
    bio = db.Column(db.Text)
    position_id = db.Column(db.Integer, db.ForeignKey(
        'position.id', ondelete='CASCADE'), nullable=False)
    votes = db.relationship('Vote', backref='candidate', lazy='dynamic',
                            passive_deletes=True, cascade="all, delete")
    result = db.relationship('Result', backref='candidate', lazy='dynamic',
                             passive_deletes=True, cascade="all, delete")

    def __repr__(self):
        return f'<Candidate {self.name} {self.position}>'

    def as_dict(self):
        return {item.name: getattr(self, item.name) for item in self.__table__.columns}


class Vote(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    position_id = db.Column(db.Integer, db.ForeignKey(
        'position.id', ondelete='CASCADE'), nullable=False)
    candidate_id = db.Column(db.Integer, db.ForeignKey(
        'candidate.id', ondelete='CASCADE'), nullable=False)
    password = db.Column(db.String())

    def __repr__(self):
        return f'<Vote {self.position.election} {self.position} {self.candidate} {self.user}>'

    def as_dict(self):
        return {item.name: getattr(self, item.name) for item in self.__table__.columns}


class Result(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    position_id = db.Column(db.ForeignKey(
        'position.id', ondelete='CASCADE'), nullable=False)
    candidate_id = db.Column(db.Integer, db.ForeignKey(
        'candidate.id', ondelete='CASCADE'), nullable=False)
    total_votes = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    modified_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Result {self.position.election} {self.position} {self.candidate}>'

    def as_dict(self):
        return {item.name: getattr(self, item.name) for item in self.__table__.columns}


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


# <=== EVENTS ===>
# listens for when Election.status_id is changed (set) then executes the given function...
# check for SQLAlchemy Events
@event.listens_for(Election.status_id, 'set')
def calculate_result(target, newvalue, oldvalue, initiator):
    # tbh, we should fetch the Status by their ids but mehn I want to reduce Database callllllssss
    # so lets hope that the Statuses have the right ids :0
    # 1 - pending
    # 2 - cancelled
    # 3 - ended
    # 4 - started
    # if Election is moving from started to ended...
    if oldvalue == eStatus.STARTED.value and newvalue == eStatus.ENDED.value:
        calculate_election_result(target, Result, db)
    # We can do more things depending on the scenario
