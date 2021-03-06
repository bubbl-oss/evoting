from dataclasses import dataclass
from app import db, login
from flask_login import UserMixin
from datetime import datetime


# @dataclass(init=False)
class Type(db.Model):
    # id: int
    # name: str

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String())  # name of type
    user = db.relationship('User', backref='type', lazy='dynamic')

    def __repr__(self):
        return f'<Type {self.name}>'

    def as_dict(self):
        return {item.name: getattr(self, item.name) for item in self.__table__.columns}


class User(UserMixin, db.Model):
    # id: int
    # email: str
    # verified: bool
    # type: Type

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


class Status(db.Model):
    # id: int
    # name: str

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable=False)
    election = db.relationship('Election', backref='status', lazy='dynamic')

    def __repr__(self):
        return f'<Status {self.name}>'

    def as_dict(self):
        return {item.name: getattr(self, item.name) for item in self.__table__.columns}


class Election(db.Model):
    # id: int
    # name: str
    # description: str
    # created_at: datetime
    # modified_at: datetime
    # owner: User.id
    # date_of_election: datetime
    # time_of_election: datetime
    # link: str
    # status: Status
    # number_of_voters: str
    # password: str

    # --- #
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    name = db.Column(db.String(), nullable=False, index=True)
    description = db.Column(db.String())
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    modified_at = db.Column(db.DateTime, default=datetime.utcnow)
    date_of_election = db.Column(db.DateTime, index=True)
    time_of_election = db.Column(db.DateTime, index=True)
    link = db.Column(db.String())
    status_id = db.Column(db.Integer, db.ForeignKey(
        'status.id'), nullable=False)
    number_of_voters = db.Column(db.String(), nullable=False)
    password = db.Column(db.String())
    candidates = db.relationship(
        'Candidate', backref='election', lazy='dynamic')
    votes = db.relationship('Vote', backref='election', lazy='dynamic')

    def __repr__(self):
        return f'<Election {self.name}>'

    def as_dict(self):
        return {item.name: getattr(self, item.name) for item in self.__table__.columns}


class Candidate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable=False, index=True)
    image = db.Column(db.String())  # should be nullable tbh
    bio = db.Column(db.Text)
    position = db.Column(db.String(200))  # should be nullable
    election_id = db.Column(db.Integer, db.ForeignKey(
        'election.id'), nullable=False)
    votes = db.relationship('Vote', backref='candidate', lazy='dynamic')

    def __repr__(self):
        return f'<Candidate {self.name}>'

    def as_dict(self):
        return {item.name: getattr(self, item.name) for item in self.__table__.columns}


# @dataclass(init=False)
class Vote(db.Model):
    # id: int
    # election: Election.id
    # candidate: Candidate.id

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    election_id = db.Column(db.Integer, db.ForeignKey(
        'election.id'), nullable=False)
    candidate_id = db.Column(db.Integer, db.ForeignKey(
        'candidate.id'), nullable=False)
    password = db.Column(db.String())

    def __repr__(self):
        return f'<Vote {self.election} {self.candidate} {self.user}>'

    def as_dict(self):
        return {item.name: getattr(self, item.name) for item in self.__table__.columns}


# flask_login stuff
@login.user_loader
def load_user(id):
    return User.query.get(int(id))
