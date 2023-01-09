import BlogApp
import os
from flask import render_template, request, Blueprint, flash, redirect, url_for
from BlogApp.models import *
from BlogApp.forms import profile_handling, private_message
from BlogApp import db, static
from BlogApp.static import profiles
from flask_login import login_required, current_user
from werkzeug.exceptions import abort
from werkzeug.utils import secure_filename

profile = Blueprint('profile', __name__)

def count_likes(blog_id):
    likers = liked_blog.query.filter_by(blog_id=blog_id).all()
    likes = len(likers)
    return likes
@profile.route("/dashboard", methods=['GET', 'POST']) 
@login_required
def dashboard():
    unread_count = 0
    for i in current_user.profile.received_messages:
        if i.read == False:
            unread_count += 1
    num_blogs = 0
    num_views = 0
    num_likes = 0
    num_comments = 0
    for i in current_user.profile.blogs:
        num_blogs += 1
        num_views += i.views
        num_likes += count_likes(i.id)
        comments = len(Comment.query.filter_by(blog_id=i.id).all())
        num_comments += comments
    num_fixed = len(Fixed.query.filter_by(user=current_user.id).all())
    num_others = len(Other.query.filter_by(user=current_user.id).all())
    return render_template('profile/dashboard.html',num_blogs=num_blogs,num_views=num_views,num_likes=num_likes,num_comments=num_comments,num_fixed=num_fixed,num_others=num_others,unread=unread_count) 

@profile.route("/account", methods=['GET', 'POST']) 
@login_required
def account():
    unread_count = 0
    for i in current_user.profile.received_messages:
        if i.read == False:
            unread_count += 1
    return render_template('profile/account.html',unread=unread_count) 


@profile.route("/personal_blogs", methods=['GET', 'POST']) 
@login_required 
def personal_blogs():
    unread_count = 0
    for i in current_user.profile.received_messages:
        if i.read == False:
            unread_count += 1
    records = Profile.query.filter_by(id=current_user.id).first().blogs.order_by(blog_data.category).all()     
    return render_template('profile/personal_blogs.html', posts=records, count_likes=count_likes,unread=unread_count) 

@profile.route("/liked_blogs", methods=['GET', 'POST'])  
@login_required
def liked_blogs():   
    records = []
    unread_count = 0
    posts_exist = False
    for i in current_user.profile.received_messages:
        if i.read == False:
            unread_count += 1
    liked_posts = liked_blog.query.filter_by(liker_id=current_user.id).all()
    ids = []
    for i in liked_posts:
        ids.append(i.blog_id)
    records=[]
    for i in ids:
        to_add = blog_data.query.filter_by(id=i).first()
        records.append(to_add)
    if len(records) != 0:
        posts_exist = True
    
    return render_template('profile/liked_blogs.html', posts=records,unread=unread_count,posts_exist=posts_exist)   


@profile.route("/ext_profile/<id>", methods=['GET', 'POST'])
@login_required
def ext_profile(id): 
    form = private_message(message='')
    records = Profile.query.filter_by(id=str(id)).first() 
    if records is None:
        flash("No profile with that ID! Please check your URL and try again!", 'red')
        return redirect(url_for('general.your_blogs'))
    elif request.method == 'POST' and form.validate_on_submit():
        message = Message(sender_id=current_user.id,recipient_id=records.id,content=form.message.data,link=str('/ext_profile/'+str(current_user.id)))
        db.session.add(message)
        db.session.commit()
        flash('Message has been sent','green')
        return render_template('profile/ext_profile.html', profile=records,form=form)      
    else:
        return render_template('profile/ext_profile.html', profile=records,form=form) 




@profile.route("/edit_profile", methods=['GET', 'POST'])
@login_required
def edit_profile():
    records = Profile.query.filter_by(id=current_user.id).first()    
    if records is None:
        abort(404)
    else:
        form = profile_handling(name=records.name, job=records.job, location=records.location, description=records.description,img=records.img,user=records,fb=records.fb,ig=records.ig,tw=records.tw)
    
    if request.method == 'POST' and form.validate_on_submit():
        records.name = form.name.data
        records.job = form.job.data
        records.location = form.location.data
        records.description = form.description.data
        if form.fb.data is None:
            records.fb = 'NIL'
        else:
            records.fb = form.fb.data
        if form.ig.data is None:
            records.ig = 'NIL'
        else:
            records.ig = form.ig.data
        if form.tw.data is None:
            records.tw = 'NIL'
        else:
            records.tw = form.tw.data
        f = form.img.data
        if f is not None and type(f) != str:
            filename = secure_filename(f.filename)
            try:
                os.makedirs('BlogApp/static/profiles/'+str(current_user.id)+'/')
            except:
                pass
            f.save(os.path.join('BlogApp', 'static', 'profiles', str(current_user.id),filename))
            records.img = str('/static/profiles/'+str(current_user.id)+'/'+str(filename))
        
        db.session.commit()
        
        
        return redirect(url_for('profile.account'))
    
    return render_template('profile/edit_profile.html', form=form)  
            


@profile.route("/delete_profile", methods=['POST'])         
@login_required 
def delete_profile(): 
    user = Auth.query.filter_by(id=current_user.id).first()
    user.deleted = True
    db.session.commit()
    flash('Successfully deleted profile', 'green')
    return redirect(url_for('auth.logout'))
