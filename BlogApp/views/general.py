import json, os
from flask import render_template, request, Blueprint, redirect, url_for
from flask_login import login_required, current_user
from BlogApp.utilities.calculate import calculate, Time
#from BlogApp.forms import study1#, study2
from BlogApp.forms import *
from BlogApp.models import *
from BlogApp import cache
#from BlogApp import gpt_125M, gpt_13B, gpt_27B
from BlogApp.utilities.essay_starter import *
from BlogApp.utilities.plag_checker import *
import readtime

def count_likes(blog_id):
    likers = liked_blog.query.filter_by(blog_id=blog_id).all()
    likes = len(likers)
    return likes

general = Blueprint('general', __name__)

global newsletter_subs   
newsletter_subs = []

@general.route("/", methods=['GET','POST'])
#@cache.cached(timeout=50)          #uncomment in final version
def root():
    return render_template('general/home.html')  


@general.route("/our_journey", methods=['GET','POST'])
#@cache.cached(timeout=50)          #uncomment in final version
def our_journey():
    readers = Profile.query.count()
    blogs = blog_data.query.count()
    writers = 0
    for i in Profile.query.all():
        if i.blogs.count() != 0:
            writers+=1
    return render_template('general/our_journey.html', readers=readers, blogs=blogs, writers=writers)  
 
 
@general.route("/tbfy", methods=['GET','POST'])
#@cache.cached(timeout=300)          #uncomment in final version
def tbfy():
    return render_template('general/tbfy.html')    


@general.route("/ssr", methods=['GET','POST'])    #ssr --> show subscription results
def ssr():
    newsletter_subs.append(request.form['entry'])
    if current_user.is_authenticated:
        return render_template('general/ssr.html', form=newsletter_subs)    
    else:
        return redirect(url_for('general.about_us'))
  

@general.route("/about_us", methods=['GET','POST'])  
#@cache.cached(timeout=50)   
def about_us():
    return render_template('general/about_us.html')
  
@general.route("/featured_blogs", methods=['GET', 'POST']) 
@general.route("/featured_blogs/<int:limit>", methods=['GET', 'POST'])  
def featured_blogs(limit=5): 
    records = blog_data.query.order_by(blog_data.views.desc()).limit(limit).all()
    return render_template('general/featured_blogs.html', posts=records, reading_time=reading_time, count_likes=count_likes)


def reading_time(text): 
    return readtime.of_text(str(text)).text

ROWS_PER_PAGE=2
@general.route("/your_blogs", methods=['GET', 'POST'])  
def your_blogs(): 
    tags = Tag.query.with_entities(Tag.name).order_by(Tag.name).group_by(Tag.name).all()
    page = request.args.get('page', 1, type=int)
    records = blog_data.query.order_by(blog_data.category).paginate(page=page, per_page=ROWS_PER_PAGE)
    print(records.items)
    all_blogs = blog_data.query.order_by(blog_data.category).all()
    return render_template('general/your_blogs.html', title='Minimal Blogs', posts=records, tags=tags,reading_time=reading_time, count_likes=count_likes, all_blogs = all_blogs)  


@general.route('/topic/<tag>')
@login_required
def topic(tag):
    try:
        topic = Tag.query.filter_by(name=tag).first()
    except:
        flash('Topic not found!','yellow')
        return redirect(url_for('general.your_blogs'))
    page = request.args.get('page', 1, type=int)
    records = topic.blogs.order_by(blog_data.category).paginate(page=page, per_page=ROWS_PER_PAGE)
    return render_template('general/your_blogs.html', title="#"+tag, posts=records,reading_time=reading_time, count_likes=count_likes) 


@general.route("/contact_us", methods=['GET','POST'])  
#@cache.cached(timeout=50)  
def contact_us():
    return render_template('general/contact_us.html')

@general.route("/scr", methods=['GET','POST'])    #scr --> show contact results
def scr():
    if os.path.exists("contact_data.json"):    
        with open("contact_data.json") as datafile:
            saveddata = json.load(datafile)
    else:
        saveddata = {}

    if request.method == "POST":
        saveddata[request.form['email']] = request.form

    with open("BlogApp/contact_data.json", "w") as datafile: 
        json.dump(saveddata, datafile)

    if current_user.is_authenticated:
        return render_template('general/scr.html', form=saveddata)    
    else:
        return redirect(url_for('general.about_us'))
        

@general.route("/essay_starter", methods=['GET','POST'])    
def essay_start():
    form = essay_starter(request.form)
    if request.method == 'POST' and form.validate_on_submit():
        data = generate(form.title.data, form.length.data, form.generator.data, form.temperature.data)
        data += '...'
        flash('You can proceed to close the previous window.', 'yellow')
        return render_template('general/essay_starter_results.html', output=data)
    
    flash('A larger model and a longer text length will result in an exponentially longer waiting time!', 'yellow')
    return render_template('general/essay_starter_form.html', form=form)

@general.route("/plag_check_form", methods=['GET','POST'])    
def plag_check():
    form = plag_check_form(num_res=10)
    if request.method == 'POST' and form.validate_on_submit():
        f = open("BlogApp/utilities/test.txt", "w")    
        f.write(form.content.data)
        f.close()
        
        load_dataset(form.query.data, form.num_res.data)
        plc()
        flash('Algorithm success! You can proceed to close the previous window.', 'yellow')
        return redirect(url_for('general.your_blogs'))
    
    return render_template('general/plag_check_form.html', form=form)
            

        
@general.errorhandler(404)    #404 errorhandler
@cache.cached(timeout=300) 
def not_found(error):
  return render_template("404.html") 


@general.route('/writers')
def writers():
    users = Profile.query.all()
    return render_template('/general/users.html',users=users)




  