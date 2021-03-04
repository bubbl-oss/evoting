from app import db, login
from flask_login import UserMixin
from datetime import datetime


class Type(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_type = db.Column(db.String())
    user = db.relationship('User', backref='type', lazy='dynamic')

    def __repr__(self):
        return f'<User {self.user_type}>'


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    user_type = db.Column(db.Integer, db.ForeignKey('type.id'), nullable=False)
    verified = db.Column(db.Boolean)
    election = db.relationship('Election', backref='user', lazy='dynamic')
    vote = db.relationship('Vote', backref='user', lazy='dynamic')

    def __repr__(self):
        return f'<User {self.email}>'


class Candidate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable=False, index=True)
    image = db.Column(db.String(), nullable=False)
    bio = db.Column(db.Text)
    position = db.Column(db.String(200), nullable=False)
    election_id = db.Column(db.Integer, db.ForeignKey(
        'election.id'), nullable=False)
    vote = db.relationship('Vote', backref='candidates', lazy='dynamic')

    def __repr__(self):
        return f'<Candidate {self.name}>'


class Status(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.String(), nullable=False)
    election = db.relationship('Election', backref='status', lazy='dynamic')

    def __repr__(self):
        return f'<Status {self.status}>'


class Election(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    owner = db.Column(db.Integer, db.ForeignKey('user.id'))
    name_of_election = db.Column(db.String(), nullable=False, index=True)
    description = db.Column(db.String())
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    modified_at = db.Column(db.DateTime, default=datetime.utcnow)
    date_of_election = db.Column(db.DateTime)
    time_of_election = db.Column(db.DateTime)
    link = db.Column(db.String())
    status_id = db.Column(db.Integer, db.ForeignKey(
        'status.id'), nullable=False)
    number_of_voters = db.Column(db.String(), nullable=False)
    password = db.Column(db.String())
    candidate = db.relationship('Candidate', backref='election', lazy='dynamic')
    vote = db.relationship('Vote', backref='election', lazy='dynamic')

    def __repr__(self):
        return f'<Election {self.name_of_election}>'


class Vote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.ForeignKey('user.id'), nullable=True)
    election_id = db.Column(db.Integer, db.ForeignKey(
        'election.id'), nullable=False)
    candidate_id = db.Column(db.Integer, db.ForeignKey(
        'candidate.id'), nullable=False)
    password = db.Column(db.String())

    def __repr__(self):
        return f'<Vote {self.id}>'


# flask_login stuff
@login.user_loader
def load_user(id):
    return User.query.get(int(id))
