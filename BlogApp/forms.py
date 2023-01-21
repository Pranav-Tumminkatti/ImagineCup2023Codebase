from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import StringField, TextAreaField, BooleanField, PasswordField
from wtforms.fields import DateField, IntegerField
from wtforms.fields import RadioField, SelectField, DecimalField
from flask import flash
from wtforms.validators import InputRequired, ValidationError, DataRequired, Length, Email, EqualTo, NumberRange
import email_validator
from BlogApp.models import Auth

class Post(FlaskForm):
  category = StringField("Category", validators=[InputRequired(), Length(max=50)])
  title = StringField("Title", validators=[InputRequired(), Length(max=200)])
  content = TextAreaField("Content", validators=[InputRequired(), Length(min=50)])
  tags = StringField("Tags (delimit each tag with a comma)")
  img = FileField('Upload optional picture for blog',validators=[FileAllowed(['jpg','JPG','png','PNG','jpeg','JPEG'])])
  grammar_checker = BooleanField('Grammar Checker')
  
  def validate_tags(form, field):
    validated = True  
    if field.data != '' and (field.data[-1] == ',' or field.data[-1] == ' '):
      form.tags.errors.append("You cannot end with a comma or a space! Please adhere to the specified guidelines")
      validated = False
    return validated


class Login(FlaskForm):
  username = StringField('Username', validators=[DataRequired()])
  password = PasswordField('Password', validators=[DataRequired()])
  remember_me = BooleanField('Remember Me') 
  
  def validate_username(form, field):
    validated = True  
    user = Auth.query.filter_by(username = form.username.data).first()
    if user is None:
      form.username.errors.append("No such user! Check your username and try again!")
      validated = False
    
    if user is not None and user.deleted == True:
      form.username.errors.append("This user has already been deleted from the database! Please check your credentials and try again!")
      validated = False
      
    return validated
      
  def validate_password(form, field):
    validated = True  
    user = Auth.query.filter_by(username = form.username.data).first()
    if user is None:
      validated = False
    else:
      if not user.check_password(form.password.data):
        form.password.errors.append("Wrong password! Try again!")
        validated = False
    return validated


class Sign_up(FlaskForm):
  username = StringField('Username', validators=[DataRequired(), Length(max=50)])
  email = StringField('Email', validators=[DataRequired(), Email()])
  password = PasswordField('Password', validators=[DataRequired(), EqualTo('confirm', message='Passwords must match')])
  confirm  = PasswordField('Confirm Password')
  
  def validate_username(form, field):
    validated = True  
    user = Auth.query.filter_by(username = form.username.data).first()
    if user is not None:
      form.username.errors.append("This username already exists! Please choose another one!")
      validated = False
    return validated
  
  def validate_email(form, field):
    validated = True  
    user = Auth.query.filter_by(email = form.email.data).first()
    if user is not None:
      form.email.errors.append("An account with that email already exists! Please log into your account.")
      validated = False
    return validated
  
  def validate_password(form, field):
    validated = True  
    if len(field.data) < 6:
      form.password.errors.append("Length of password must be at least 6 characters!")
      validated = False
    
    if not any(char.isdigit() for char in field.data):
      form.password.errors.append("Password should contain at least 1 numerical character!")
      validated = False
      
    if not any(c in "!.@#$%^&*()-+?_=,<>/" for c in field.data):
      form.password.errors.append("Password should contain at least 1 special character!")
      validated = False
      
    return validated
  
  def validate_confirm(form, field):
    validated = True  
    if form.password.data != form.confirm.data:
      form.confirm.errors.append("Passwords don't match, please try again.")
      validated = False
    return validated
  

class profile_handling(FlaskForm):
  name = StringField("Name", validators=[InputRequired(), Length(max=50)])
  job = StringField("Job", validators=[InputRequired(), Length(max=100)])
  location = StringField("Location", validators=[InputRequired(), Length(max=200)])
  description = TextAreaField("Description", validators=[InputRequired(), Length(max=500)])
  fb = StringField("Facebook Profile link")
  ig = StringField("Instagram Profile link")
  tw = StringField("Twitter Profile link")
  img = FileField('Upload Profile Picture',validators=[FileAllowed(['jpg','JPG','png','PNG','jpeg','JPEG'])])

class study1(FlaskForm):
  notes = TextAreaField("Notes")
  start_time = BooleanField('Do you have a start time and end time?')
  fixed = IntegerField('Fixed',validators=[NumberRange(min=0),InputRequired()])
  others = IntegerField('Others',validators=[NumberRange(min=0),InputRequired()])
  p = RadioField('Based on',validators=[InputRequired()], choices = ['Importance','Urgency'])

class EmailForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])

class PasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired(), EqualTo('confirm', message='Passwords must match')])
    confirm  = PasswordField('Repeat Password')
    
    def validate_password(form, field):
      validated = True  
      if len(field.data) < 6:
        form.password.errors.append("Length of password must be at least 6 characters!")
        validated = False
      
      if not any(char.isdigit() for char in field.data):
        form.password.errors.append("Password should contain at least 1 numerical character!")
        validated = False
        
      if not any(c in "!.@#$%^&*()-+?_=,<>/" for c in field.data):
        form.password.errors.append("Password should contain at least 1 special character!")
        validated = False
        
      return validated
  
    def validate_confirm(form, field):
      validated = True  
      if form.password.data != form.confirm.data:
        form.confirm.errors.append("Passwords don't match, please try again.")
        validated = False
      return validated
      
class essay_starter(FlaskForm):
  generator = SelectField("Generator", choices=[('gpt_125M','gpt3-neo 125M'), ('gpt_13B','gpt3-neo 1.3B'), ('gpt_27B','gpt3-neo 2.7B')], validators=[InputRequired()])
  title = StringField("Title", validators=[InputRequired(), Length(min=10)])
  length = IntegerField("Length of text", validators=[InputRequired(), NumberRange(min=10)])
  temperature = DecimalField("Temperature", validators=[InputRequired(), NumberRange(min=0.1, max=0.99)], places=2)
  
class comment_form(FlaskForm):
  comment = TextAreaField('Leave a comment', validators=[DataRequired()])

class plag_check_form(FlaskForm):
  query = StringField('Search Query', validators=[DataRequired()])
  content = TextAreaField("Content", validators=[DataRequired(), Length(min=100)])
  num_res = IntegerField("Accuracy", validators=[InputRequired(), NumberRange(min=5, max=50)])
  
class edit_comment(FlaskForm):
  new = StringField('Update your comment', validators = [DataRequired()])

class private_message(FlaskForm):
  message = TextAreaField(validators=[DataRequired()])



class Add_appointment(FlaskForm):
  doctor = IntegerField("Doctor id",validators=[InputRequired()])
  clinic = IntegerField("Clinic id",validators=[InputRequired()])
  start_time = StringField('Start time',validators=[InputRequired(),Length(min=4,max=4)])
  end_time = StringField('End time',validators=[InputRequired(),Length(min=4,max=4)])

class Add_doctor(FlaskForm):
  doctor = StringField("Doctor's username",validators=[InputRequired()])
  clinic = IntegerField("Clinic id",validators=[InputRequired()])

class Add_medicine(FlaskForm):
  name = StringField("Name",validators=[InputRequired()])
  stock = IntegerField("Units available (stock)",validators=[InputRequired()])
  puc = StringField("Price per unit ($)",validators=[InputRequired()])

class Login_client(FlaskForm):
  username = StringField("ID",validators=[InputRequired()])
  email = StringField("Email",validators=[InputRequired(),Email()])
  password = PasswordField("Password",validators=[InputRequired()])

class Login_user(FlaskForm):
  username = StringField("ID",validators=[InputRequired()])
  email = StringField("Email",validators=[InputRequired(),Email()])
  password = PasswordField("Password",validators=[InputRequired()])

class Find_slot(FlaskForm):
  start_time = StringField('Start time',validators=[InputRequired(),Length(min=4,max=4)])
  end_time = StringField('End time',validators=[InputRequired(),Length(min=4,max=4)])