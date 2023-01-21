from flask import render_template, request, url_for, redirect, Blueprint, flash
from werkzeug.exceptions import abort
from BlogApp import db
from BlogApp.forms import Login_client, Add_appointment, Add_doctor
from flask_login import login_required, current_user

appointments = Blueprint('appointments', __name__)

@appointments.route("/client_login",methods=['GET','POST'])
def client_login():
  return render_template('appointments/client_login.html',form = Login_client())

@appointments.route('/client_signup',methods=['GET','POST'])
def client_signup():
  return render_template('appointments/client_signup.html')

@appointments.route('/clinic',methods=['GET','POST'])
@login_required
def clinic():
  return render_template('appointments/clinic.html')

@appointments.route('/pharmacy',methods=['GET','POST'])
@login_required
def pharmacy():
  return render_template('appointments/pharmacy.html')

@appointments.route('/find_clinic',methods=['GET','POST'])
#@login_required
def find_c():
  return render_template('appointments/find_clinic.html')

@appointments.route('/find_doctor',methods=['GET','POST'])
#@login_required
def find_d():
  return render_template('appointments/find_doctor.html')

@appointments.route('/find_slot',methods=['GET','POST'])
#@login_required
def find_s():
  return render_template('appointments/find_slot.html')

@appointments.route('/add_appointment',methods=['GET','POST'])
#@login_required
def add_a():
  return render_template('appointments/add_appointment.html',form=Add_appointment())

@appointments.route('/add_doctor',methods=['GET','POST'])
@login_required
def add_d():
  return render_template('appointments/add_doctor.html',form=Add_doctor())

