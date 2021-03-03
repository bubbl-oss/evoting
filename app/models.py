from app import db
from datetime import datetime

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    election = db.relationship('Election', backref='user', lazy=True)
    vote = db.relationship('Vote', backref='user', lazy=True)

    def __repr__(self):
        return f'<User {self.username}>'

class Candidate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable=False)
    image = db.Column(db.String(), nullable=False)
    bio = db.Column(db.Text)
    position = db.Column(db.String(200), nullable=False)
    election_id = db.Column(db.Integer, db.ForeignKey('election.id'), nullable=False) 
    vote = db.relationship('Vote', backref='candidate', lazy=True)

    def __repr__(self):
        return f'<Candidate {self.name}>'

class Status(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.String(), nullable=False)
    election = db.relationship('Election', backref='status', lazy=True)

    def __repr__(self):
        return f'<Status {self.status}>'

class Election(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name_of_election = db.Column(db.String(), nullable=False)
    time = db.Column(db.DateTime, default=datetime.utcnow)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    published = db.Column(db.Boolean)
    link = db.Column(db.String())
    status_id = db.Column(db.Integer, db.ForeignKey('status.id'), nullable=False)
    number_of_voters = db.Column(db.String(), nullable=False)
    candidate = db.relationship('Candidate', backref='election', lazy=True)

    def __repr__(self):
        return f'<Election {self.name_of_election}>'

class Vote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.ForeignKey('user.id'), nullable=True)
    election_id = db.Column(db.Integer, db.ForeignKey('election.id'), nullable=False)
    candidate_id = db.Column(db.Integer, db.ForeignKey('candidate.id'), nullable=False)