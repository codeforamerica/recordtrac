__author__ = 'jcastillo'
from flask.ext.wtf import Form
from wtforms import StringField, SelectField, TextAreaField, DateField, SubmitField
from wtforms_components import PhoneNumberField, Email
from wtforms.validators import DataRequired, Length, Email, Regexp, EqualTo
from wtforms import ValidationError
from flask.ext.login import current_user

class OfflineRequestForm(Form):
    request_text = TextAreaField(u'<i class="icon-exclamation-sign"></i>&nbsp;Request Description', validators=[
        DataRequired('The request description is required'),
        Length(1, 5000, 'Your request must be less than 5000 characters')])
    request_format = SelectField(u'Format Received', choices=[(' ', ''), ('Fax', 'Fax'), ('Phone', 'Phone'),
                                                              ('Email', 'Email'), ('Mail', 'Mail'),
                                                              ('In-Person', 'In-Person'),
                                                              ('Text Message', 'Text Message'), ('311', '311')],
                                 validators=[DataRequired('You must enter a request format')], default=' ')
    request_date = DateField(u'Request Date', format='%m/%d/%Y',
                             validators=[DataRequired('You must enter the request date')])
    request_department = SelectField(u'Request Department', choices=[
        (' ', ''),
        ('OCME', 'Chief Medical Examiner'), ('DOE', 'Department of Education'),
        ('DORIS', 'Department of Records and Information Services'),
        ('DOITT', 'Info. Tech. and Telecom.'), ('OOM', 'Mayor\'s Office')],
        validators=[DataRequired('Please choose a department')], default=' ')
    request_name = StringField(u'Requester\'s Name', validators=[DataRequired('Please enter the requestor\'s name')])
    request_email = StringField(u'Requester\'s Email', validators=[Email('Please enter a valid email address')])
    request_phone = PhoneNumberField(u'Requester\'s Phone Number')
    request_fax = PhoneNumberField(u'Requester\'s Fax Number')
    request_address_street = StringField(u'Requester\'s Street Address')
    request_address_city = StringField(u'Requester\'s City')
    request_address_state = SelectField(u'Requester\'s State', choices=[
        ('', ''),
        ('AL', 'Alabama'), ('AK', 'Alaska'), ('AZ', 'Arizona'), ('AR', 'Arkansas'),
        ('CA', 'California'), ('CO', 'Colorado'), ('CT', 'Connecticut'), ('DE', 'Delaware'),
        ('DC', 'District Of Columbia'), ('FL', 'Florida'), ('GA', 'Georgia'), ('HI', 'Hawaii'),
        ('ID', 'Idaho'), ('IL', 'Illinois'), ('IN', 'Indiana'), ('IA', 'Iowa'),
        ('KS', 'Kansas'), ('KY', 'Kentucky'), ('LA', 'Louisiana'), ('ME', 'Maine'),
        ('MD', 'Maryland'), ('MA', 'Massachusetts'), ('MI', 'Michigan'), ('MN', 'Minnesota'),
        ('MS', 'Mississippi'), ('MO', 'Missouri'), ('MT', 'Montana'), ('NE', 'Nebraska'),
        ('NV', 'Nevada'), ('NH', 'New Hampshire'), ('NJ', 'New Jersey'), ('NM', 'New Mexico'),
        ('NY', 'New York'), ('NC', 'North Carolina'), ('ND', 'North Dakota'), ('OH', 'Ohio'),
        ('OK', 'Oklahoma'), ('OR', 'Oregon'), ('PA', 'Pennsylvania'), ('RI', 'Rhode Island'),
        ('SC', 'South Carolina'), ('SD', 'South Dakota'), ('TN', 'Tennessee'), ('TX', 'Texas'),
        ('UT', 'Utah'), ('VT', 'Vermont'), ('VA', 'Virginia'), ('WA', 'Washington'),
        ('WV', 'West Virginia'), ('WI', 'Wisconsin'), ('WY', 'Wyoming')], default='NY')
    request_address_zip = StringField(u'Requester\'s Zip Code', validators=[
        Length(5, 5, 'Please enter the five-digit zip code')])
    request_submit = SubmitField(u'Submit Request')


class NewRequestForm(Form):
    request_text = TextAreaField(u'<i class="icon-exclamation-sign"></i>Request Description', validators=[
        DataRequired('The request description is required'),
        Length(1, 5000, 'Your request must be less than 5000 characters')])
    request_department = SelectField(u'Request Department', choices=[
        ('OCME', 'Chief Medical Examiner'), ('DOE', 'Department of Education'),
        ('DORIS', 'Department of Records and Information Services'),
        ('DOITT', 'Info. Tech. and Telecom.'), ('OOM', 'Mayor\'s Office')],
        validators=[DataRequired('Please choose a department')])
    request_name = StringField(u'Requester\'s Name', validators=[DataRequired('Please enter the your name')])
    request_email = StringField(u'Requester\'s Email', validators=[Email('Please enter a valid email address')])
    request_phone = PhoneNumberField(u'Requester\'s Phone Number')
    request_fax = PhoneNumberField(u'Requester\'s Fax Number')
    request_address_street = StringField(u'Requester\'s Street Address')
    request_address_city = StringField(u'Requester\'s City')
    request_address_state = SelectField(u'Requester\'s State', choices=[
        ('AL', 'Alabama'), ('AK', 'Alaska'), ('AZ', 'Arizona'), ('AR', 'Arkansas'),
        ('CA', 'California'), ('CO', 'Colorado'), ('CT', 'Connecticut'), ('DE', 'Delaware'),
        ('DC', 'District Of Columbia'), ('FL', 'Florida'), ('GA', 'Georgia'), ('HI', 'Hawaii'),
        ('ID', 'Idaho'), ('IL', 'Illinois'), ('IN', 'Indiana'), ('IA', 'Iowa'),
        ('KS', 'Kansas'), ('KY', 'Kentucky'), ('LA', 'Louisiana'), ('ME', 'Maine'),
        ('MD', 'Maryland'), ('MA', 'Massachusetts'), ('MI', 'Michigan'), ('MN', 'Minnesota'),
        ('MS', 'Mississippi'), ('MO', 'Missouri'), ('MT', 'Montana'), ('NE', 'Nebraska'),
        ('NV', 'Nevada'), ('NH', 'New Hampshire'), ('NJ', 'New Jersey'), ('NM', 'New Mexico'),
        ('NY', 'New York'), ('NC', 'North Carolina'), ('ND', 'North Dakota'), ('OH', 'Ohio'),
        ('OK', 'Oklahoma'), ('OR', 'Oregon'), ('PA', 'Pennsylvania'), ('RI', 'Rhode Island'),
        ('SC', 'South Carolina'), ('SD', 'South Dakota'), ('TN', 'Tennessee'), ('TX', 'Texas'),
        ('UT', 'Utah'), ('VT', 'Vermont'), ('VA', 'Virginia'), ('WA', 'Washington'),
        ('WV', 'West Virginia'), ('WI', 'Wisconsin'), ('WY', 'Wyoming')])
    request_address_zip = StringField(u'Requester\'s Zip Code', validators=[
        Length(5, 5, 'Please enter the five-digit zip code')])
    request_submit = SubmitField(u'Submit Request')
