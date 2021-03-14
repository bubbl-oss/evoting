from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SelectField, SubmitField, PasswordField, TextAreaField, RadioField
from wtforms.fields.core import FieldList, FormField
from wtforms.fields.html5 import DateTimeLocalField
from wtforms.validators import DataRequired
from app.models import Status


class CandidateForm(FlaskForm):
    name = StringField('Name')
    bio = TextAreaField('Bio')
    submit = SubmitField('Submit')


class ElectionForm(FlaskForm):
    name = StringField(
        'Election Name', validators=[DataRequired()])
    description = TextAreaField('Election Description')
    starting_at = DateTimeLocalField(
        'Date and Time of Election', format='%Y-%m-%dT%H:%M')
    # TODO: this is temporary. We will add the supplied time to the start date and just save it
    ending_at = DateTimeLocalField(
        'Duration of Election', format='%Y-%m-%dT%H:%M')
    # candidates = FieldList(FormField(CandidateForm),
    #                        min_entries=2, max_entries=10)
    number_of_voters = IntegerField(
        'Number of Voters', validators=[DataRequired()])
    password = StringField('Password')
    submit = SubmitField('Submit')


class PositionForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    description = TextAreaField('Position Description')
    submit = SubmitField('Submit')


class VotePasswordForm(FlaskForm):
    password = StringField('Password')
    submit = SubmitField('Continue')


class VotingForm(FlaskForm):
    candidates = RadioField('Candidates', choices=[], coerce=str)
    submit = SubmitField('Vote')
