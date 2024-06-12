from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, TextAreaField, SelectField, FileField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length
from flask_wtf.file import FileAllowed
from flask_app.models import Section

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=4)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

class SectionForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    description = TextAreaField('Description')
    submit = SubmitField('Add Section')

class BookForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    pdf = FileField('PDF', validators=[DataRequired(), FileAllowed(['pdf'], 'Only PDF files are allowed.')])
    authors = StringField('Authors', validators=[DataRequired()])
    section = SelectField('Section', validators=[DataRequired()], coerce=int)

    def __init__(self):
        super(BookForm, self).__init__()
        self.section.choices = [(section.id, section.name) for section in Section.query.all()]

    submit = SubmitField('Add Book')

