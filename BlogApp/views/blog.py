from flask import render_template, request, Blueprint, url_for, redirect, flash
from werkzeug.exceptions import abort
from werkzeug.utils import secure_filename
from BlogApp import db
from BlogApp.forms import *
from BlogApp.models import *
from BlogApp.utilities.plag_checker import *
from BlogApp.utilities.summarizer import *
from BlogApp.utilities.grammar_checker import *
import datetime
from datetime import datetime
from flask_login import login_required, current_user
import readtime
import os
blog = Blueprint('blog', __name__)

def count_likes(blog_id):
    likers = liked_blog.query.filter_by(blog_id=blog_id).all()
    likes = len(likers)
    return likes


def count_dislikes(blog_id):
    dislikers = disliked_blog.query.filter_by(blog_id=blog_id).all()
    dislikes = len(dislikers)
    return dislikes

@blog.route("/display_personal_post/<id>", methods=['GET', 'POST'])  
@login_required  
def display_personal_post(id):
    id = str(id)
    post_data = Profile.query.filter_by(id=current_user.id).first().blogs.filter_by(id=id).first()   
    if post_data is None:
        flash("No blog with that ID belongs to you! Please check your URL and try again!", 'red')
        return redirect(url_for('profile.personal_blogs'))
    else:    
        return render_template('blog/display_personal_post.html', post=post_data)  


@blog.route("/display_post/<id>", methods=['GET', 'POST'])    
@login_required
def display_post(id):
    form = comment_form()
    if request.method == 'POST':
        new = Comment(blog_id=int(id), profile_id=current_user.id, comment=form.comment.data,time = str('Posted on ' + str(datetime.now())))
        post = blog_data.query.filter_by(id=int(id)).first()
        author_message = Message(sender_id=current_user.id,recipient_id=post.author.id,content=(str(current_user.username)+' just commented on your blog "'+str(post.title)+'"'+str(form.comment.data)+'". View profile:'),link=str('/display_post/'+str(post.id)))
        db.session.add(author_message)
        db.session.add(new)
        db.session.commit()
        return redirect(url_for('blog.display_post', id=id) + '#ld')  
        
    id = str(id)
    post_data = blog_data.query.filter_by(id=id).first() 
      
    if post_data: 
        
        next_blog = blog_data.query.filter_by(id=(int(id)+1)).first()  
        prev_blog = blog_data.query.filter_by(id=(int(id)-1)).first()  
        
        post_views = post_data.views
        post_views += 1
        post_data.views = post_views
        db.session.commit()
        
        if post_data.author.id == current_user.id:
            is_owner=True
        else:
            is_owner=False

        is_liked = False
        liked = liked_blog.query.filter_by(blog_id=id).all()
        if liked is not None:
            for i in liked:
                if i.liker_id == current_user.id: 
                    is_liked = True
                    break
    
        is_disliked = False
        disliked = disliked_blog.query.filter_by(blog_id=id).all()
        if disliked is not None:
            for i in disliked:
                if i.disliker_id == current_user.id: 
                    is_disliked = True
                    break
        try:
            disliked = disliked_blog.query.filter_by(blog_id=id).first_or_404()
            is_disliked = True
        except:
            pass
        
        comments = Comment.query.filter_by(blog_id=int(id)).all()
        comments = comments[::-1]
        
        return render_template('blog/display_post.html', post=post_data, next_blog=next_blog, prev_blog=prev_blog, is_owner=is_owner, is_liked=is_liked, is_disliked=is_disliked, comments=comments,  form=form, current_user = current_user,likes = count_likes(id), dislikes = count_dislikes(id))
    else:
        #flash("No blog with that ID! Please check your URL and try again!", 'red')  #this piece of code is being run for no reason idk why
        return redirect(url_for('general.your_blogs'))  


@blog.route("/like_post/<id>", methods=['GET', 'POST']) 
@login_required   
def like_post(id):
    id = str(id)
    liked = Profile.query.filter_by(id=current_user.id).first().liked_blogs
    post = blog_data.query.filter_by(id=id).first()
    to_like = liked_blog(blog_id=id,liker_id=current_user.id)
    db.session.add(to_like)
    try:
        disliked = disliked_blog.query.filter_by(blog_id=id).first_or_404()
        db.session.delete(disliked)
    except:
        pass
    db.session.commit()
    author_message =Message(sender_id=current_user.id,recipient_id=post.author.id,content=(str(current_user.username)+' just liked your post "'+str(post.title)+'". View it here:'),link=str('/display_post/'+str(post.id)))
    db.session.add(author_message)    
    db.session.commit()
    return redirect('/display_post/'+id+'#ld')
    
    
@blog.route("/un_like_post/<id>", methods=['GET', 'POST'])   
@login_required 
def un_like_post(id):
    id = str(id)
    post = blog_data.query.filter_by(id=id).first()
    liked = liked_blog.query.filter_by(blog_id=id).first()
    db.session.delete(liked)
    db.session.commit()
    author_message =Message(sender_id=current_user.id,recipient_id=post.author.id,content=(str(current_user.username)+' just un-liked your blog "'+str(post.title)+'". View it here:'),link=str('/display_post/'+str(post.id)))
    db.session.add(author_message)
    db.session.commit()
    return redirect('/display_post/'+id+"#ld")


@blog.route("/dislike_post/<id>", methods=['GET', 'POST'])  
@login_required  
def dislike_post(id):
    id = str(id)
    post = blog_data.query.filter_by(id=id).first()
    to_dislike = disliked_blog(blog_id=int(id),disliker_id=current_user.id)
    db.session.add(to_dislike)
    try:
        liked = liked_blog.query.filter_by(blog_id=id).first_or_404()
        db.session.delete(liked)
    except:
        pass
    db.session.commit()
    author_message =Message(sender_id=current_user.id,recipient_id=post.author.id,content=(str(current_user.username)+' just disliked your post "'+str(post.title)+'". View it here:'),link=str('/display_post/'+str(post.id)))
    db.session.add(author_message)    
    db.session.commit()
    return redirect('/display_post/'+id+"#ld")


@blog.route("/un_dislike_post/<id>", methods=['GET', 'POST'])    
@login_required
def un_dislike_post(id):
    id = str(id)
    post = blog_data.query.filter_by(id=id).first()
    disliked = disliked_blog.query.filter_by(blog_id=id).first()
    db.session.delete(disliked)
    
    author_message =Message(sender_id=current_user.id,recipient_id=post.author.id,content=(str(current_user.username)+' just un-disliked your blog "'+str(post.title)+'". View it here:'),link=str('/display_post/'+str(post.id)))
    db.session.add(author_message)
    db.session.commit()
    return redirect('/display_post/'+id+"#ld")
        
@blog.route("/plag_check/<id>", methods=['GET', 'POST'])
@login_required
def plag_check(id):
    blog = blog_data.query.filter_by(id=id).first()
    if blog is None:
        flash("No blog with that ID! Please check your URL again!", 'red')
        return redirect(url_for('general.your_blogs'))
    elif blog.author.id != current_user.id:
        flash('You cannot check for plagarism in a post that does not belong to you!', 'red')
        return redirect(url_for('profile.personal_blogs'))    
    else:
        if len(blog.content) >= 100:
            
            if os.path.exists('BlogApp/utilities/test.txt'):
                with open("BlogApp/utilities/test.txt") as f:
                    contents = f.read()
                f.close()
                
                blog_content = blog.content
                for ch in ["\r\n",'\r','\n']:
                        if ch in blog_content:
                            blog_content=blog_content.replace(ch,"")
                
                if (blog_content in contents or contents in blog_content) and (os.path.exists('BlogApp/utilities/train.txt')):
                    plc()
                else:
                    f = open("BlogApp/utilities/test.txt", "w")    
                    f.write(blog_content)
                    f.close()
                    
                    search_query = str(blog.category) + ' ' + str(blog.title)
                    load_dataset(search_query, 10)
                    plc()
            else:
                f = open("BlogApp/utilities/test.txt", "w")    
                f.write(blog.content)
                f.close()
                
                search_query = str(blog.category) + ' ' + str(blog.title)
                load_dataset(search_query, 10)
                plc()
                
            flash('Algorithm success! You can proceed to close the previous window.', 'yellow')
            return redirect(url_for('blog.display_post', id=id))
        else:
            flash('Unable to test dataset as it is too small. Minimum word count: 100 words!', 'yellow')
            return redirect(url_for('blog.display_post', id=id))
    
    
@blog.route("/create_post", methods=['GET', 'POST'])   
@login_required 
def create_post():    
    form = Post()     
    if request.method  == 'POST' and form.validate_on_submit():
        owner = Auth.query.filter_by(id=current_user.id).first().profile
        try:
            synop = generate_summary(correct_text(form.content.data)['result'],1)
        except:
            synop = "Error 404. Something went terribly wrong. Please contact us for assistance. We sincerely apologise for the inconvenience caused!"
        post = blog_data(category=form.category.data, title=form.title.data, content=form.content.data, synopsis=synop, author=owner)
        f = form.img.data
        if f is not None and type(f) != str:
            filename = secure_filename(f.filename)
            records = blog_data.query.all()
            try:
                os.makedirs('BlogApp/static/blogs/'+str(len(records)+1)+'/')
            except:
                pass
            f.save(os.path.join('BlogApp', 'static', 'blogs', str(len(records)+1),filename))
            post.img = str('/static/blogs/'+str(len(records)+1)+'/'+str(filename))
        
        db.session.add(post)
        db.session.commit()
        
        if form.tags.data != None:
            tags = [tag.strip() for tag in form.tags.data.split(",")]
            
            for tag in tags:
                #find out if this user already created this tag already
                tag_for_blog = Tag.query.filter_by(blog_id = post.id, name = tag).first()
                
                if not tag_for_blog:
                    newtag = Tag(name=tag, blog_id = post.id) #create new tag
                    db.session.add(newtag) #add to db
                    db.session.commit() #commit to db
                    post.tags.append(newtag) #add newtag to current newtodo
                else:
                    post.tags.append(tag_for_blog)
                
                db.session.commit()
        message = Message(sender_id=1,recipient_id=current_user.id,content="You just published a blog! '"+str(post.title)+"Check it out here:",link="/display_post/"+str(post.id))
        db.session.add(message)
        db.session.commit()
        flash('Success! Your post has been published!', 'green')
        
        if form.grammar_checker.data == True:
            return redirect(url_for('blog.gc_df', id=post.id))
        else:
            return redirect(url_for('blog.display_post', id=post.id))    
    else: 
        return render_template('blog/create_post.html', form=form) 
  

@blog.route("/edit_post/<id>", methods=['GET', 'POST'])  
@login_required 
def edit_post(id):
    id = str(id)
    post_data = blog_data.query.filter_by(id=id).first() 
    if post_data is None:
        flash("No blog with that ID! Please check your URL again!", 'red')
        return redirect(url_for('general.your_blogs'))
    elif post_data.author.id != current_user.id:
        flash('You cannot edit a post that does not belong to you!', 'red')
        return redirect(url_for('profile.personal_blogs'))
    else:
        tgs = []
        tags = post_data.tags
        for item in tags:
            tgs.append(item.name)
        form = Post(category=post_data.category, title=post_data.title, content=post_data.content, synopsis=post_data.synopsis, tags= ", ".join(tgs))
        
    if request.method  == 'POST' and form.validate_on_submit():  
        post_data.category = form.category.data
        post_data.title = form.title.data
        post_data.content = form.content.data
        f = form.img.data
        if f is not None and type(f) != str:
            filename = secure_filename(f.filename)
            records = blog_data.query.all()
            try:
                os.makedirs('BlogApp/static/blogs/'+str(len(records)+1)+'/')
            except:
                pass
            f.save(os.path.join('BlogApp', 'static', 'blogs', str(len(records)+1),filename))
            post_data.img = str('/static/blogs/'+str(len(records)+1)+'/'+str(filename))
            
        post_data.tags = []
        if form.tags.data != None:
            tags = [tag.strip() for tag in form.tags.data.split(",")]
            
            for tag in tags:
                #find out if this user already created this tag already
                tag_for_blog = Tag.query.filter_by(blog_id = post_data.id, name = tag).first()
                
                if not tag_for_blog:
                    newtag = Tag(name=tag, blog_id = post_data.id) #create new tag
                    db.session.add(newtag) #add to db
                    db.session.commit() #commit to db
                    post_data.tags.append(newtag) #add newtag to current newtodo
                else:
                    post_data.tags.append(tag_for_blog)
                    
                db.session.commit()
        message = Message(sender_id=1,recipient_id=current_user.id,content="You just edited your blog! '"+str(post_data.title)+"Check it out here:",link="/display_post/"+str(post_data.id))
        db.session.add(message)
        db.session.commit()
        flash("Success! Blog has been edited!", 'green')
        return redirect(url_for('blog.display_post', id=id))

    return render_template('blog/edit_post.html', form=form, post_data=post_data)  
  

@blog.route("/delete_post/<id>", methods=['POST', 'GET'])   
@login_required
def delete_post(id):                                
    id = str(id)
    post_data = blog_data.query.filter_by(id=id).first()    #only post request is accepted so 404 should never be called technically, just a safety measure 
    if post_data is None:
        flash("No blog with that ID! Please check your URL again!", 'red')
    else:
        db.session.delete(post_data)
        db.session.commit()  
        flash('Blog successfully deleted!', 'green')
        
    return redirect(url_for('general.your_blogs'))


@blog.route("/gc_df/<id>", methods=['POST', 'GET'])     #implement another route directly in navbar
@login_required
def gc_df(id):
    id = str(id)
    blog = blog_data.query.filter_by(id=id).first()
    if blog is None:
        flash("No blog with that ID! Please check your URL again!", 'red')
        return redirect(url_for('general.your_blogs'))
    else:
        try:
            table_html = generate_df(blog.content)
            
            corrected = correct_text(blog.content)
            blog.content = corrected['result']
            db.session.commit()
            
            return render_template('blog/gc_df_template.html', table=table_html, item=blog)
        except:
            flash("That is one flawless blog! Well done!", 'blue')
            return redirect(url_for('blog.display_post', id=id))
     
@blog.route('/edit_comment/<id>',methods=['GET','POST'])
@login_required
def edit_c(id):
    if request.method == 'GET':
        try:
            prev = request.args['prev']
        except:
            flash('method not allowed','red')
            return redirect('/')
    comment = Comment.query.filter_by(id=id).first()
    form  = edit_comment(new = comment.comment)
    if request.method == 'POST' and form.validate_on_submit():
        print('updated')
        prev = request.form['prev']
        comment.comment = form.new.data
        old = comment.time[10:10+len('2021-08-26 19:52:34.461011')]
        comment.time = str('Posted on ' + old + ', Updated on '+str(datetime.now()))
        db.session.add(comment)
        db.session.commit()
        return redirect('/display_post/' + str(prev) + '#ld')
    return render_template('blog/edit_comment.html',form=form,id=id, prev=prev)


@blog.route('/your_comments')
@login_required
def your_comments():
    unread_count = 0
    for i in current_user.profile.received_messages:
        if i.read == False:
            unread_count += 1
    comments = Comment.query.filter_by(profile_id=current_user.id).all()
    return render_template('profile/your_comments.html',comments=comments,unread=unread_count)

@blog.route("/delete_comment/<id>", methods=['POST', 'GET'])   
@login_required
def delete_comment(id):
    if request.method == 'GET':
        prev = None
        try:
            prev = request.args['prev']
        except:
            flash('Method not allowed','red')
            return redirect('/your_blogs')
        comment = Comment.query.filter_by(id=id).first()
        if comment.profile_id != current_user.id:
            flash('You cannot edit someone else\'s comment. Don\'t do that. It doesn\'t look good on you.','red')
            return redirect('/display_post/'+str(prev))
        if comment is None:
            flash("No comment with that ID! Please check your URL again!", 'red')
        else:
            db.session.delete(comment)
            db.session.commit()
            flash('Comment successfully deleted!', 'green')
    else:
        flash('Method not allowed','red')
    return redirect('/display_post/'+str(prev) + '#ld')

#route for exporting the blog as pdf --> incomplete
# @blog.route('/blog<id>.pdf')
# @login_required
# def pdf(id):
    #post = blog_data.query.filter_by(id=id).first()
    #html = render_template('display_post.html',post=post)
    #return render_pdf(HTML(string=html))









