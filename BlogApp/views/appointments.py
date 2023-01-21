from flask import render_template, request, url_for, redirect, Blueprint, flash
from werkzeug.exceptions import abort
from BlogApp import db
from BlogApp.forms import Login_client, Add_appointment, Add_doctor

appointments = Blueprint('appointments', __name__)

@appointments.route("/",methods=['GET','POST'])
def root():
  return render_template('about.html')

@appointments.route("/client_login",methods=['GET','POST'])
def client_login():
  return render_template('client_login.html',form = Login_client())

@appointments.route('/client_signup',methods=['GET','POST'])
def client_signup():
  return render_template('client_signup.html')

@appointments.route('/clinic',methods=['GET','POST'])
def clinic():
  return render_template('clinic.html')

@appointments.route('/pharmacy',methods=['GET','POST'])
def pharmacy():
  return render_template('pharmacy.html')

@appointments.route('/user_login',methods=['GET','POST'])
def user_login():
  return render_template('user_login.html')

@appointments.route('/user',methods=['GET','POST'])
def user():
  return render_template('user.html')

@appointments.route('/findslot',methods=['GET','POST'])
def find():
  return render_template('find_a_slot.html')

@appointments.route('/add_appointment',methods=['GET','POST'])
def add_a():
  return render_template('add_appointment.html',form=Add_appointment())

@appointments.route('/add_doctor',methods=['GET','POST'])
def add_d():
  return render_template('add_doctor.html',form=Add_doctor())

