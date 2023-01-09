from flask import render_template, request, url_for, redirect, Blueprint, flash
from werkzeug.exceptions import abort
from BlogApp import db

from flask_login import login_required, fresh_login_required, login_user, logout_user, current_user
from werkzeug.urls import url_parse
from wtforms.validators import ValidationError
import datetime

from BlogApp.utilities.token import generate_confirmation_token, confirm_token,ts
from BlogApp.forms import Login, Sign_up, EmailForm, PasswordForm
from BlogApp.models import Auth, Profile
from BlogApp.utilities.email import send_email
from BlogApp.utilities.decorators import check_confirmed
auth = Blueprint('auth', __name__)

@auth.route("/login", methods = ["POST", "GET"])
def login():
    if current_user.is_authenticated == False:
        form = Login()
        
        if request.method == "POST" and form.validate_on_submit():
            user = Auth.query.filter_by(username = form.username.data).first()  
            login_user(user, remember=form.remember_me.data)
            flash('Successfully logged in!', 'green')
            next_page = request.args.get("next")  #gets data from the GET url. For example a user tries to access index without logging in: the url will show "next='index'" which will redirect the user to the page that he wanted to go to before logging in
            if not next_page or url_parse(next_page).netloc != "":  #if the url is one that is in the views.py, the netloc component of url_parse will be empty
                next_page = url_for('profile.dashboard')
            return redirect(next_page)
        return render_template("auth/login.html", form = form)
    else:
        flash('Already logged in!', 'red')
        return redirect(url_for('profile.dashboard'))

@auth.route("/sign_up", methods = ["POST", "GET"])
def sign_up():
    if current_user.is_authenticated == False:
        form = Sign_up()
        if request.method == 'POST' and form.validate_on_submit():
            new_user = Auth(username=form.username.data, email=form.email.data,confirmed=False)
            new_user.set_password(form.password.data)
            db.session.add(new_user)
            new_user_profile = Profile(name=form.username.data, job='What you do', location='25.0000° N, 71.0000° W', description='Totally short and optional description about yourself, what you do and so on.', user=new_user) 
            db.session.add(new_user_profile)
            db.session.commit()
            
            token = generate_confirmation_token(form.email.data)
            confirm_url = url_for('auth.confirm_email', token=token, _external=True)
            html = render_template('auth/activate.html', confirm_url=confirm_url)
            subject = "Please confirm your email"
            send_email(new_user.email, subject, html)
            flash('A confirmation email has been sent via email. Please confirm your email as soon as possible so you can reset your password if you forget it.', 'green')
            return redirect(url_for('auth.login'))
        return render_template('auth/sign_up.html', form=form)
    
    else:
        flash('Already logged in!', 'red')
        return redirect(url_for('general.root'))


@auth.route("/logout", methods = ["POST", "GET"])
@login_required
def logout():
  logout_user()
  flash("Successfully logged out!", "green") 
  return redirect(url_for("general.root"))

@auth.route('/unconfirmed')
def unconfirmed():
    try:
        user = Auth.query.filter_by(id=current_user.id).first_or_404()
        if user.confirmed:
            return redirect('/')
    except:
        pass
    return render_template('auth/unconfirmed.html')

@auth.route('/confirm/<token>') #confirm the external token
def confirm_email(token):
    try:
        email = confirm_token(token)
    except:
        flash('The confirmation link is invalid or has expired.', 'red')
        return redirect(url_for("auth.unconfirmed"))            
    user = Auth.query.filter_by(email=email).first_or_404()
    if user.confirmed:      #check because you are editing the Confirmed table not the confirm column in the auth table
        if current_user.is_authenticated:
            flash('Account already confirmed','green')
            return redirect('/')
        else:
            flash('Account already confirmed. Please login.', 'green')
            return redirect('/login')
    else:
        user.confirmed = True
        db.session.commit()
        flash('You have confirmed your account email. Thanks!', 'green')
        return redirect(url_for("general.root"))
    

@auth.route('/resend')
@login_required
def resend_confirmation():
    #user = Auth.query.filter_by(id=current_user.id).first_or_404()
    token = generate_confirmation_token(current_user.email)
    confirm_url = url_for('auth.confirm_email', token=token, _external=True)
    html = render_template('Auth/activate.html', confirm_url=confirm_url)
    subject = "Please confirm your email"
    send_email(current_user.email, subject, html)
    flash('A new confirmation email has been sent.', 'green')
    return redirect(url_for("auth.unconfirmed"))

#passwords
@auth.route('/reset', methods=["GET", "POST"])
def reset():
    form = EmailForm()
    '''
    try:
        print(form.email.data)
        print(form.validate_on_submit())
        print(form.errors)
    except:
        print('cannot')
    '''
    if current_user.is_authenticated:
        subject = "Password reset requested"
        # Here we use the URLSafeTimedSerializer we created in `utilities` at the
        # beginning of the chapter
        token = ts.dumps(current_user.email, salt='recover-key')
        recover_url = url_for(
            'auth.reset_with_token',
            token=token,
            _external=True)
        html = render_template('auth/recover.html',recover_url=recover_url)
        send_email(str(current_user.email), subject, html)
        print('email sent')
        return redirect(url_for('auth.r_e_s'))
    if form.validate_on_submit() and request.method == 'POST':
        print('submit')
        try:
          user = Auth.query.filter_by(email=form.email.data).first_or_404()
          print('found')
        except:
          flash('No such user. Please register for an account first','red')
          print('no user')
          return redirect('/sign_up')
        print(user)
        print(user.confirmed)
        if user.confirmed == False:
          print('no')
          return redirect('/unconfirmed')
        subject = "Password reset requested"
        # Here we use the URLSafeTimedSerializer we created in `utilities` at the
        # beginning of the chapter
        token = ts.dumps(user.email, salt='recover-key')
        recover_url = url_for(
            'auth.reset_with_token',
            token=token,
            _external=True)
        html = render_template('auth/recover.html',recover_url=recover_url)
        send_email(str(user.email), subject, html)
        print('email sent')
        return redirect(url_for('auth.r_e_s'))
    '''
    else:
        print('er')
        flash('No such email.','red')
    '''
    return render_template('auth/reset.html', form=form)

@auth.route('/recovery_email_sent')
def r_e_s():
  return render_template('auth/passwordemailsent.html')


@auth.route('/reset/<token>', methods=["GET", "POST"])
def reset_with_token(token):
    try:
        email = ts.loads(token, salt="recover-key", max_age=86400)
    except:
        abort(404)

    form = PasswordForm()

    if form.validate_on_submit():
        user = Auth.query.filter_by(email=email).first_or_404()

        user.set_password(form.password.data)
        #db.session.add(user) dont add the user, just update password
        db.session.commit()
        print(user.password)
        flash('Password successfully changed!','green')
        return redirect(url_for('auth.login'))

    return render_template('auth/reset_with_token.html', form=form, token=token)
