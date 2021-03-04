from flask_wtf import FlaskForm
from wtforms import StringField, SelectMultipleField, SelectField, DateField, DateTimeField, SubmitField, PasswordField, TextAreaField
from wtforms.validators import DataRequired
from app.models import Status

class ElectionForm(FlaskForm):
    name_of_election = StringField('Election Name', validators=[DataRequired()])
    description = TextAreaField('Election Description')
    date_of_election = DateField('Date of Election', validators=[DataRequired()], format='%d-%m')
    time_of_election = DateTimeField('Time of Election', validators=[DataRequired()], format='%H:%M')
    status_id = SelectField(u'Status', coerce=int, defailt='pending')
    number_of_voters = StringField('Number of Voters', validators=[DataRequired()])
    password = PasswordField('Password')
    submit = SubmitField('Generate Link')

def status(request, id):
    status = Status.query.get(id)
    form = ElectionForm(request.POST, obj=status)
    form.status_id.choices = [(s.id, s.status) for s in Status.query.all()]