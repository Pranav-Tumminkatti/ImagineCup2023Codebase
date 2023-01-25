from flask import render_template, request, url_for, redirect, Blueprint, flash
from werkzeug.exceptions import abort
from BlogApp import db
from BlogApp.forms import Login_client, Add_appointment, Add_doctor
from flask_login import login_required, current_user
from BlogApp.models import Auth, Profile

appointments = Blueprint('appointments', __name__)

@appointments.route("/client_login",methods=['GET','POST'])
def client_login():
    if current_user.is_authenticated == False:
        form = Login()
        
        if request.method == "POST" and form.validate_on_submit():
            client = Auth.query.filter_by(username = form.username.data).first()  
            client_type = client.user_type
            login_user(client, remember=form.remember_me.data)
            flash('Successfully logged in!', 'green')
            next_page = request.args.get("next")  #gets data from the GET url. For example a user tries to access index without logging in: the url will show "next='index'" which will redirect the user to the page that he wanted to go to before logging in
            if client_type == "clinic":
              return redirect('appointments/clinic.html')
            else: 
              return redirect('appointments/pharmacy.html')
        return render_template('appointments/client_login.html',form = Login())
    else:
        flash('Already logged in!', 'red')
        return redirect(url_for('profile.dashboard'))

@appointments.route('/client_signup',methods=['GET','POST'])
def client_signup():
    if current_user.is_authenticated == False:
        form = clinet_sign_up()
        if request.method == 'POST' and form.validate_on_submit():
            new_client = Auth(username=form.username.data, email=form.email.data, phone_number = form.phone_number.data, user_type = form.user_type.data confirmed=False, )
            new_client.set_password(form.password.data)
            db.session.add(new_client)

            if form.user_type.data == "clinic":
              new_clinic = Clinic(name = form.name.data, open_time = form.open_time.data, 
              close_time = form.close_time.data, location = form.address.data, credentials = new_client)
              db.session.add(new_clinic)
            else:
              new_pharmacy = Pharmacy(name = form.name.data, open_time = form.open_time.data, 
              close_time = form.close_time.data, location = form.address.data, credentials = new_client)
              db.session.add(new_pharmacy)
            db.session.commit()
            
            '''
            token = generate_confirmation_token(form.email.data)
            confirm_url = url_for('auth.confirm_email', token=token, _external=True)
            html = render_template('auth/activate.html', confirm_url=confirm_url)
            subject = "Please confirm your email"
            send_email(new_user.email, subject, html)
            flash('A confirmation email has been sent via email. Please confirm your email as soon as possible so you can reset your password if you forget it.', 'green')
            '''
            return redirect(url_for('auth.login'))
        return render_template('appointments/client_signup.html' form = clinet_sign_up())

    
    else:
        flash('Already logged in!', 'red')
        return redirect(url_for('general.root'))

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

