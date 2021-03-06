from app import app, db
from app.models import User, Election, Candidate, Status, Type, Vote, Result, Position


@app.shell_context_processor
def define_shell_context():
    return {'db': db, 'User': User, 'Election': Election, 'Candidate': Candidate, 'Status': Status, 'Type': Type, 'Vote': Vote, 'Result': Result, 'Position': Position}
