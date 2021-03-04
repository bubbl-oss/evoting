from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SelectField, SubmitField, PasswordField, TextAreaField
from wtforms.fields.core import FieldList, FormField
from wtforms.fields.html5 import DateField, DateTimeField
from wtforms.validators import DataRequired
from app.models import Status


class CandidateForm(FlaskForm):
    name = StringField('Name')
    description = TextAreaField('Description')


class ElectionForm(FlaskForm):
    name = StringField(
        'Election Name', validators=[DataRequired()])
    description = TextAreaField('Election Description')
    date_of_election = DateField('Date of Election', format='%Y-%m-%d')
    time_of_election = DateTimeField('Time of Election', format='%H:%M')
    candidates = FieldList(FormField(CandidateForm),
                           min_entries=2, max_entries=10)
    number_of_voters = IntegerField(
        'Number of Voters', validators=[DataRequired()])
    password = PasswordField('Password')
    submit = SubmitField('Generate Link')


def status(request, id):
    status = Status.query.get(id)
    form = ElectionForm(request.POST, obj=status)
    form.status_id.choices = [(s.id, s.status) for s in Status.query.all()]
