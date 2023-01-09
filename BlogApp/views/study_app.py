import json, os
from flask import render_template, request, Blueprint, redirect, url_for, flash
from flask_login import current_user, login_required
from BlogApp.utilities.calculate import calculate, Time
from BlogApp.forms import study1 #, study2
from BlogApp.models import *
from BlogApp import db
from sqlalchemy import delete

study_app = Blueprint('study_app', __name__)

len_o = 0
len_f = 0
final_f = []
final_o = []
fixed = []
other = []
schedule_made = False
new_schedule = False
results_has_been_visited = False
@study_app.route('/studytools',methods=['GET','POST'])
@login_required
def study():
    global fixed
    global other
    global schedule_made
    global new_schedule
    global results_has_been_visited
    records = Auth.query.filter_by(id=current_user.id).first().profile
    if request.method == 'POST':
      to_delete = Fixed.query.filter_by(user=current_user.id).all()
      print(to_delete)
      for i in to_delete:
        db.session.delete(i)
      to_delete = Other.query.filter_by(user=current_user.id).all()
      for i in to_delete:
        db.session.delete(i)
      for i in range(len_f):
        print(request.form['fixed'+str(i)])
        new = Fixed(user = records.id, name = request.form['fixed'+str(i)], start = str(request.form['start'+str(i)]), end = str(request.form['end'+str(i)]))
        db.session.add(new)
      for i in range(len_o):
        new = Other(user = records.id, name = request.form['other'+str(i)], est = request.form['est'+str(i)], priority = request.form['rank'+str(i)])
        db.session.add(new)
      new = Schedule_Made(user = current_user.id)
      db.session.add(new)
      db.session.commit()
      if results_has_been_visited:
        message = Message(sender_id = 1, recipient_id = current_user.id, content = 'You created a new schedule.',link='/studytools')
        db.session.add(message)
        db.session.commit()
      results_has_been_visited = False
    fixed = Fixed.query.filter_by(user=current_user.id).order_by(Fixed.start).all()
    other = Other.query.filter_by(user=current_user.id).order_by(Other.est).all()
    schedulemade = Schedule_Made.query.filter_by(user=current_user.id).first()
    print(current_user.id)
    print(Schedule_Made)
    if schedulemade == None:
      schedule_made = False
    else:
      schedule_made = True
    return render_template('study_app/studytools.html', profile=records,schedule_made = schedule_made,fixed = fixed, other = other, len_o= len(other),len_f=len(fixed))

@study_app.route('/studytools/scheduler',methods=['GET','POST'])
def schedule():
    form = study1()
    return render_template('study_app/schedule.html',form=form,stage=1)

@study_app.route('/studytools/scheduler/input',methods=['GET','POST'])
def schedule2():
  start = True
  try:
    start=request.args['start_time']
    start=True
  except:
    start= False
  try:
    num_fixed = int(request.args['fixed'])
    num_others = int(request.args['others'])
    notes = str(request.args['notes'])
  except:
    form = study1()
    flash('You need to enter some more basic data first!','red')
    return render_template('study_app/schedule.html',form=form,stage=1)
  if len(str(request.args['fixed'])) == 0 or len(str(request.args['others'])) == 0:
    form = study1()
    flash('Fill in all fields.','red')
    return render_template('study_app/schedule.html',form=form,stage=1)
  try:
    priority = request.args['p']
  except:
    form = study1()
    flash('Fill in all fields.','red')
    return render_template('study_app/schedule.html',form=form,stage=1)
  if num_fixed <= 0 and num_others <= 0:
    form = study1()
    flash('You must have at least one event in your schedule.','red')
    return render_template('study_app/schedule.html',form=form,stage=1)
  return render_template('study_app/schedule.html',stage=2,num_fixed=num_fixed,num_others=num_others,notes=notes,start=start,priority = priority,error_message = '')

@study_app.route('/studytools/scheduler/results',methods=['POST'])
def schedule3():
  start_t = Time(0,0)
  end_t = Time(23,59)
  fixed=[]
  others=[]
  try:
    start = bool(request.form['start'])
  except:
    start = False
  try:
    num_fixed = int(request.form['num_fixed'])
  except:
    num_fixed = 0
  try:
    num_others = int(request.form['num_others'])
  except:
    num_others = 0
  if start:
    start_t = Time(int(request.form['starttime_h']),int(request.form['starttime_m']))
    end_t = Time(int(request.form['endtime_h']),int(request.form['endtime_m']))
    if (end_t < start_t or end_t == start_t):
      flash('An End Time cannot be equal to or before a Start Time.','red')
      return render_template('study_app/schedule.html',stage=2,start = start, notes = str(request.form['notes']), num_fixed = num_fixed,num_others = num_others)
  for i in range(num_fixed):
    begin = Time(int(request.form['start_h'+str(i)]),int(request.form['start_m'+str(i)]))
    end = Time(int(request.form['end_h'+str(i)]),int(request.form['end_m'+str(i)]))
    if (end < begin or end == begin):
      flash('An End Time cannot be equal to or before a Start Time.','red')
      return render_template('study_app/schedule.html',stage=2,start = start, notes = str(request.form['notes']), num_fixed = num_fixed,num_others = num_others)
    else:
      fixed.append({'start_h':str(begin.get_h()),'start_m':str(begin.get_m()),'end_h':str(end.get_h()),'end_m':str(end.get_m()),'name':str(request.form['event'+str(i)])})
  for i in range(num_others):
    others.append({'name':request.form['other'+str(i)],'est_h':int(request.form['hour'+str(i)]),'est_m':int(request.form['minute'+str(i)]),'rank':int(request.form['rank'+str(i)])})
  result = calculate(start_t,end_t,fixed,others)
  print(result[0])
  print(result[1])
  global len_f
  len_f = len(result[0])
  print(len_f)
  global len_o
  len_o = len(result[1])
  print(len_o)
  global results_has_been_visited
  results_has_been_visited = True
  return render_template('/study_app/schedule.html',num_fixed = num_fixed,num_others = num_others,fixed = result[0], other = result[1],stage=3)