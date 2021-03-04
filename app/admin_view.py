from app import db, admin
from app.models import Type, User, Candidate, Election, Vote, Status
from flask_admin.contrib.sqla import ModelView


admin.add_view(ModelView(User, db.session))
admin.add_view(ModelView(Type, db.session))
admin.add_view(ModelView(Candidate, db.session))
admin.add_view(ModelView(Election, db.session))
admin.add_view(ModelView(Vote, db.session))
admin.add_view(ModelView(Status, db.session))