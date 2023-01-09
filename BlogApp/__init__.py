from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_caching import Cache
from flask_mail import Mail
#from flask_images import Images
from transformers import pipeline
from werkzeug.utils import secure_filename
#from flask_debugtoolbar import DebugToolbarExtension

app = Flask(__name__)
UPLOAD_FOLDER = '/BlogApp/static/profiles'
app.secret_key = "thisisasecret"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

#db
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///app.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
db = SQLAlchemy(app)

app.config.update(dict(
    DEBUG = True,
    MAIL_SERVER = 'smtp.gmail.com',
    MAIL_PORT = 465,
    MAIL_USE_TLS = False,
    MAIL_USE_SSL = True,
    MAIL_USERNAME = 'unveiled.email.confirmation@gmail.com',
    MAIL_PASSWORD = 'unveiledunveiled',
    MAIL_DEFAULT_SENDER = 'unveiled.email.confirmation@gmail.com'
))

#email conformation
mail = Mail(app)
app.config['SECURITY_PASSWORD_SALT']= 'my_precious_two'
app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = 'unveiled.email.confirmation@gmail.com'  # enter your email here
app.config['MAIL_DEFAULT_SENDER'] = 'unveiled.email.confirmation@gmail.com' # enter your email here
app.config['MAIL_PASSWORD'] = 'unveiledunveiled' # enter your password here

#login
login = LoginManager(app)
login.login_view = "auth.login" #points to the function login in views.py
login.login_message = "Login/Sign Up to view the previous page!"
login.login_message_category = "yellow" 

#caching
cache = Cache(app, config={
    "DEBUG": True,          
    "CACHE_TYPE": "SimpleCache", 
    "CACHE_DEFAULT_TIMEOUT": 300
}) 

#Flask-Images
#images = Images(app)
#limiting image upload size
app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024 * 3 #3MB, 1024 * 1024 = 1MB

#flask debug toolbar extension
#toolbar = DebugToolbarExtension(app)
app.config['DEBUG_TB_INTERCEPT_REDIRECTS']= False

'''
#gpt3-neo language models
gpt_125M = pipeline('text-generation', model='EleutherAI/gpt-neo-125M')
gpt_13B = pipeline('text-generation', model='EleutherAI/gpt-neo-1.3B')
gpt_27B = pipeline('text-generation', model='EleutherAI/gpt-neo-2.7B')
'''


from BlogApp import models
import os
@app.cli.command("initdb") #use this to backup db data to excel file
def reset_db():
  ''' Reset the database with dummy data '''
  db.drop_all()
  db.create_all()
  models.insert_dummy_data(db)
  
  cache.clear()
  
  if os.path.exists("BlogApp/contact_data.json"):
    os.remove("BlogApp/contact_data.json")

'''
@app.cli.command("backupdb")      #cli command to backup db to excel file
def backup_db():
  #Backup the database
  import csv
  outfile = open('mydump.csv', 'w')
  outcsv = csv.writer(outfile)
  records = session.query(MyModel).all()    #error
  [outcsv.writerow([getattr(curr, column.name) for column in app.__mapper__.columns]) for curr in records]
  # or maybe use outcsv.writerows(records)

  outfile.close()
'''

#register blueprints
from BlogApp.views.auth import auth
from BlogApp.views.blog import blog
from BlogApp.views.general import general
from BlogApp.views.profile import profile
from BlogApp.views.study_app import study_app
from BlogApp.views.messages import message

app.register_blueprint(general)
app.register_blueprint(auth)
app.register_blueprint(blog)
app.register_blueprint(profile)
app.register_blueprint(study_app)
app.register_blueprint(message)