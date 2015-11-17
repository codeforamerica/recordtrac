from flask.ext.wtf import Form
from wtforms import StringField, SelectField, TextAreaField, DateField, \
    BooleanField, PasswordField, SubmitField, FileField
from wtforms_components import PhoneNumberField
from wtforms.validators import DataRequired, Length, Email
from flask import Flask
from flask_recaptcha import ReCaptcha

from public_records_portal import db, models

__author__ = 'jcastillo'

app = Flask(__name__)

agencies = [
    (r.name, r.name) for r in db.session.query(models.Department).all()
    ]
agencies.insert(0, ('', ''))

categories = [
    ('', ''),
    ('Business', 'Business'),
    ('Civic Services', 'Civic Services'),
    ('Culture & Recreation', 'Culture & Recreation'),
    ('Education', 'Education'),
    ('Government Administration', 'Government Administration'),
    ('Environment', 'Environment'),
    ('Health', 'Health'),
    ('Housing & Development', 'Housing & Development'),
    ('Public Safety', 'Public Safety'),
    ('Social Services', 'Social Services'),
    ('Transportation', 'Transportation')
]

formats = [
    ('', ''),
    ('Fax', 'Fax'),
    ('Phone', 'Phone'),
    ('Email', 'Email'),
    ('Mail', 'Mail'),
    ('In-Person', 'In-Person'),
    ('Text Message', 'Text Message'),
    ('311', '311')
]

states = [
    ('', ''),
    ('AL', 'Alabama'),
    ('AK', 'Alaska'),
    ('AZ', 'Arizona'),
    ('AR', 'Arkansas'),
    ('CA', 'California'),
    ('CO', 'Colorado'),
    ('CT', 'Connecticut'),
    ('DE', 'Delaware'),
    ('DC', 'District Of Columbia'),
    ('FL', 'Florida'),
    ('GA', 'Georgia'),
    ('HI', 'Hawaii'),
    ('ID', 'Idaho'),
    ('IL', 'Illinois'),
    ('IN', 'Indiana'),
    ('IA', 'Iowa'),
    ('KS', 'Kansas'),
    ('KY', 'Kentucky'),
    ('LA', 'Louisiana'),
    ('ME', 'Maine'),
    ('MD', 'Maryland'),
    ('MA', 'Massachusetts'),
    ('MI', 'Michigan'),
    ('MN', 'Minnesota'),
    ('MS', 'Mississippi'),
    ('MO', 'Missouri'),
    ('MT', 'Montana'),
    ('NE', 'Nebraska'),
    ('NV', 'Nevada'),
    ('NH', 'New Hampshire'),
    ('NJ', 'New Jersey'),
    ('NM', 'New Mexico'),
    ('NY', 'New York'),
    ('NC', 'North Carolina'),
    ('ND', 'North Dakota'),
    ('OH', 'Ohio'),
    ('OK', 'Oklahoma'),
    ('OR', 'Oregon'),
    ('PA', 'Pennsylvania'),
    ('RI', 'Rhode Island'),
    ('SC', 'South Carolina'),
    ('SD', 'South Dakota'),
    ('TN', 'Tennessee'),
    ('TX', 'Texas'),
    ('UT', 'Utah'),
    ('VT', 'Vermont'),
    ('VA', 'Virginia'),
    ('WA', 'Washington'),
    ('WV', 'West Virginia'),
    ('WI', 'Wisconsin'),
    ('WY', 'Wyoming')
]


class OfflineRequestForm(Form):
    request_category = SelectField(u'Category*', choices=categories,
                                   validators=[
                                       DataRequired(
                                           'The request category '
                                           'is required')])
    request_agency = SelectField(u'Agency*', choices=agencies,
                                 validators=[
                                     DataRequired('Please select an agency')],
                                 default='')
    request_summary = TextAreaField(u'Summary*',
                                    validators=[
                                        DataRequired(
                                            'You must enter a '
                                            'summary of your request'),
                                        Length(1, 250,
                                               'Your request summary '
                                               'must be less '
                                               'than 250 characters')])
    request_text = TextAreaField(u'Detailed Description*', validators=[
        Length(1, 5000,
               'The detailed description of this request must be less than '
               '5000 characters')])
    request_attachment_description = TextAreaField(u'Description of Attachment', validators=[Length(1,5000,'less than 5000 characters')])
    request_attachment = FileField(u'Upload attachment')
    request_format = SelectField(u'Format Received*', choices=formats,
                                 validators=[
                                     DataRequired(
                                         'You must enter the format in '
                                         'which the request was received')],
                                 default='')
    request_date = DateField(u'Request Date*', format='%m/%d/%Y',
                             validators=[DataRequired(
                                 'You must enter the date this request '
                                 'was received.')])
    request_first_name = StringField(u'First Name*',
                                     validators=[DataRequired(
                                         'Please enter the requestor\'s '
                                         'first name')])
    request_last_name = StringField(u'Last Name*', validators=[
        DataRequired('Please enter the requestor\'s last name')])
    request_role = StringField(u'Role/Title')
    request_organization = StringField(u'Organization')
    request_email = StringField(u'Email', validators=[
        Email('Please enter a valid email address')])
    request_phone = PhoneNumberField(u'Phone Number')
    request_fax = PhoneNumberField(u'Fax Number')
    request_address_street_one = StringField(u'Address Line 1')
    request_address_street_two = StringField(u'Address Line 2')
    request_address_city = StringField(u'City')
    request_address_state = SelectField(u'State', choices=states, default='NY')
    request_address_zip = StringField(u'Zip Code',
                                      validators=[Length(5, 5,
                                                         'Please enter '
                                                         'your five-digit '
                                                         'zip code')])
    recaptcha = ReCaptcha(app)
    terms_of_use = BooleanField(
        u'I acknowledge that I have read and accepted the Terms of Use for '
        u' this application, as stated above',
        validators=[DataRequired('You must accept the terms of use')])
    request_submit = SubmitField(u'Submit Request')


class NewRequestForm(Form):
    request_category = SelectField(u'Category*', choices=categories,
                                   validators=[DataRequired(
                                       'The request category is required')])
    request_agency = SelectField(u'Agency*', choices=agencies, validators=[
        DataRequired('Please select an agency')],
                                 default='')
    request_summary = TextAreaField(u'Summary*', validators=[
        DataRequired('You must enter a summary of your request'),
        Length(1, 250,
               'Your request summary must be less than 250 characters')])
    request_text = TextAreaField(u'Detailed Description*', validators=[
        Length(1, 5000,
               'The detailed description of this request must be less than'
               ' 5000 characters')])
    request_first_name = StringField(u'First Name*',
                                     validators=[DataRequired(
                                         'Please enter the requestor\'s'
                                         ' first name')])
    request_last_name = StringField(u'Last Name*', validators=[
        DataRequired('Please enter the requestor\'s last name')])
    request_role = StringField(u'Role/Title')
    request_organization = StringField(u'Organization')
    request_email = StringField(u'Email', validators=[
        Email('Please enter a valid email address')])
    request_phone = PhoneNumberField(u'Phone Number')
    request_fax = PhoneNumberField(u'Fax Number')
    request_address_street_one = StringField(u'Address Line 1')
    request_address_street_two = StringField(u'Address Line 2')
    request_address_city = StringField(u'City')
    request_address_state = SelectField(u'State', choices=states, default='NY')
    request_address_zip = StringField(u'Zip Code',
                                      validators=[Length(5, 5,
                                                         'Please enter '
                                                         'your five-digit '
                                                         'zip code')])
    recaptcha = ReCaptcha(app)
    terms_of_use = BooleanField(
        u'I acknowledge that I have read and accepted the Terms of Use for '
        u'this application, as stated above',
        validators=[DataRequired('You must accept the terms of use')])
    request_submit = SubmitField(u'Submit Request')


class LoginForm(Form):
    username = StringField('Email', validators=[DataRequired(), Length(1, 64)])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Log In')

class EditUserForm(Form):
    username = StringField('Email', validators=[DataRequired(), Length(1, 64)])
    phone = StringField('Phone Number', validators=[DataRequired()])
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    title = StringField('Title', validators=[DataRequired()])

    submit = SubmitField('Update')
