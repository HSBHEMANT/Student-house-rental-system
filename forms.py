from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import (
    StringField,
    PasswordField,
    SelectField,
    TextAreaField,
    FloatField,
    DateField,
    SubmitField,
    MultipleFileField,
)
from wtforms.validators import DataRequired, Email, Length, NumberRange, ValidationError, Optional
from models import User


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=20)])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Sign In')


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone = StringField('Phone Number', validators=[Length(max=20)])
    role = SelectField(
        'I am a',
        choices=[
            ('student', 'Student looking for housing'),
            ('owner', 'Property owner/landlord')
        ],
        validators=[DataRequired()]
    )
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username already exists. Please choose a different one.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email already registered. Please choose a different one.')


class PropertyForm(FlaskForm):
    title = StringField('Property Title', validators=[DataRequired(), Length(max=200)])
    description = TextAreaField('Description', validators=[Length(max=1000)])
    location = StringField('Location', validators=[DataRequired(), Length(max=200)])
    rent = FloatField('Monthly Rent (₹)', validators=[DataRequired(), NumberRange(min=0)])
    room_type = SelectField(
        'Room Type',
        choices=[
            ('single', 'Single Room'),
            ('shared', 'Shared Room'),
            ('studio', 'Studio'),
            ('apartment', 'Full Apartment')
        ],
        validators=[DataRequired()]
    )
    facilities = TextAreaField('Facilities (one per line)')
    images = MultipleFileField(
        'Property Images',
        validators=[FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 'Images only!')]
    )
    submit = SubmitField('Save Property')


class SearchForm(FlaskForm):
    location = StringField('Location', validators=[Optional()])
    min_rent = FloatField('Min Rent (₹)', validators=[Optional(), NumberRange(min=0)])
    max_rent = FloatField('Max Rent (₹)', validators=[Optional(), NumberRange(min=0)])
    room_type = SelectField(
        'Room Type',
        choices=[
            ('', 'Any'),
            ('single', 'Single Room'),
            ('shared', 'Shared Room'),
            ('studio', 'Studio'),
            ('apartment', 'Full Apartment')
        ]
    )
    submit = SubmitField('Search')


class BookingForm(FlaskForm):
    check_in_date = DateField('Check-in Date', validators=[DataRequired()])
    check_out_date = DateField('Check-out Date', validators=[DataRequired()])
    notes = TextAreaField('Additional Notes')
    submit = SubmitField('Book Property')

    def validate_check_out_date(self, check_out_date):
        if check_out_date.data <= self.check_in_date.data:
            raise ValidationError('Check-out date must be after check-in date.')
