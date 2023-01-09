from flask import render_template, Blueprint
from flask_login import login_required, current_user
from BlogApp.models import *

message = Blueprint('Message',__name__)

@message.route('/messages',methods=['GET','POST'])
@login_required
def messages():
    user = Profile.query.filter_by(id=current_user.id).first()
    unread_count = 0
    for i in user.received_messages:
        if i.read == False:
            unread_count += 1
    received_messages = user.received_messages
    received_messages = received_messages[::-1]
    sent_messages = user.sent_messages
    sent_messages = sent_messages[::-1]
    return render_template('/messaging/messages.html',sent_messages=sent_messages,received_messages=received_messages, user=user,unread=unread_count)

@message.route('/view_message/<id>')
@login_required
def viewmessage(id):
    user = Profile.query.filter_by(id=current_user.id).first()
    unauthorised=False
    try:
        message  = Message.query.filter_by(id=id).first_or_404()
        no_exist = False
        if message.re.id != current_user.id:
            unauthorised=True
        if not unauthorised:
            message.read = True
            db.session.commit()
    except:
        message = 0
        no_exist = True

    return render_template('/messaging/display_message.html',message=message,no_exist=no_exist,user=user,unauthorised=unauthorised)