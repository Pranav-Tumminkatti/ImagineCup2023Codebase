class Time(object):
  #the basic function for defining a class. Each object has an hours and a minutes property
  def __init__(self,hours,minutes):
    self.hours = int(hours)
    self.minutes = int(minutes)
  #defining getter methods
  def get_h(self):
    return self.hours
  def get_m(self):
    return self.minutes
    # *no setter methods are necessary for this app
  #To add 2 times together, we need to add both hours and minutes
  #then we update the new time so that minutes < 60
  def __add__(self,new):
    a = self.get_h() + new.get_h()
    b = self.get_m() + new.get_m()
    #if minutes is >= 60, it will adjust so that every 60 minutes is converted to an hour.
    a += b//60
    b = b%60
    return Time(a,b)
  #to subtract one time from another
  def __sub__(self,new):
    a = self.get_h() - new.get_h()
    b = self.get_m() - new.get_m()
    #returns the subtracted time if both hours and minutes > 0. Also adjusts so that minutes < 60
    if a >= 0 and b >= 0:
      a += b//60
      b = b%60
      return Time(a,b)
    #if hours is less than 0 but minutes is more than 60...
    elif a < 0 and b >= 60:
      #we will check if the number of minutes is enough to make up the number of 'negative' hours.
      #e.g.  -1 hours and 60 minutes would altogether result in 0 hours and 0 minutes.
      #-2 hours and 60 minutes would result in -1 hours
      #-1 hours and 120 minutes would result in 60 min = 1 hour
      a += abs(b//60)
      b = abs(b%60)
      #if hours is still less than 0 even after adding all the 'hours'
      if a < 0:
        return 0
      #but if the Time is valid and both hours and minutes are positive, it returns the time
      else:
        return Time(a,b)
    #if a < 0 and b < 60, there is no possibility that the time is valid and real
    elif a < 0:
      return 0
    #if minutes < 0 and hours == 0, since you cannot have negative minutes only return 0
    elif a == 0 and b < 0:
      return 0
    #if minutes < 0 BUT hours > 0, it is possible that the hours, when converted to minutes...
    #would make the minutes positive
    #e.g. 2 hours and -100 minutes = 20 minutes
    elif a > 0 and b < 0:
      b += (a*60)
      a //= 60
      if b < 0:
        return 0
      else:
        return Time(a,b)
  #to print a Time object during development of the app.
  def __str__(self):
    return str(self.hours).zfill(2) + ':' + str(self.minutes).zfill(2)
  #to return a Time object
  def __repr__(self):
    return str(self.hours).zfill(2) + ':' + str(self.minutes).zfill(2)
  #to check if two Time objects are equal or not. Both hours and minutes need to be equal.
  #we ensure that minutes < 60 and the appropriate number of hours is added.
  def __eq__(self,new):
    a = Time(self.get_h() + (self.get_m()//60), self.get_m()%60)
    b = Time(new.get_h() + (new.get_m()//60), new.get_m()%60)
    return ((a.get_h() == b.get_h()) and (a.get_m() == b.get_m()))
  #to check if two Time objects are not equal to each other.
  #if either the hours or the minutes are different, the two Times are different
  #we ensure that minutes < 60 and the appropriate number of hours is added.
  def __ne__(self,new):
    a = Time(self.get_h() + (self.get_m()//60), self.get_m()%60)
    b = Time(new.get_h() + (new.get_m()//60), new.get_m()%60)
    return ((a.get_h() != b.get_h()) or (a.get_m() != b.get_m()))
  def __lt__(self,new):
    a = new - self
    if type(a) != int:
      return 1
    else:
      return 0
#This is the function to fit the 'other' events into the slots of Time in between the 'fixed' events
#it takes in the start_time and end_time
#it is a separate function because I coded it on the Python Desktop IDE before linking it to Flask and Web App things

def calculate(start_t,end_t,fixed,others):
  slots = []
  for i in others:
    i['est'] = Time(i['est_h'],i['est_m'])
  for i in fixed:
    i['start'] = Time(i['start_h'],i['start_m'])
    i['end'] = Time(i['end_h'],i['end_m'])
  if fixed != []:
    fixed = sorted(fixed, key = lambda i:i['start'])
    if type(fixed[0]['start'] - start_t) == int:
      start_t = fixed[0]['start']
    else:
      slots.append([start_t,fixed[0]['start']])
    if type(end_t - fixed[-1]['end']) == int:
      end_t = fixed[-1]['end']
    else:
      slots.append([fixed[-1]['end'],end_t])
    for i in range(len(fixed)-1):
      slots.append([fixed[i]['end'],fixed[i+1]['start']])
  if len(slots) == 0:
    slots.append([start_t,end_t])
  others = sorted(others, key = lambda i:i['rank'], reverse = 1)
  checked = []
  used = []
  time_left = Time(0,0)
  print(fixed)
  print(others)
  for period in slots:
    print('period:'+str(period))
    done = False
    others = sorted(others, key = lambda i:i['rank'], reverse = 1)
    checked.clear()
    #start the while loop
    #if done == True, the while loop stops
    while not done:
      #set time_left to the length of the period.
      #period[0] is the start time of the slot, period[1] is the end time of the slot
      time_left = period[1] - period[0]
      print(time_left)
      #if time_left is not 00:00, and you have tasks to complete (there could be nothing in 'others' if the user did not provide any)
      if time_left != Time(0,0) and len(others) != 0:
        #create a counter to keep track of how far through 'others' we have gone through
        counter = 0
        #for each item in others,
        for i in others:
          #increase the counter by 1
          counter += 1
          #if we have not checked this item
          if i not in checked:
            #if i has not already been added to the schedule, and the item can 'fit' into the schedule (ie. the time this item requires does not exceed time_left)
            if (i not in used) and (type(time_left - i['est']) != int):
              #we put this item into the schedule
              fixed.append({'start':period[0],'end':period[0] + i['est'], 'name':i['name']})
              #we subtract from the amount of time we hav left
              time_left -= i['est']
              #and we make the start time of the period later, so that when we reset time_left later at the start of the while loop, the time left is correct
              period[0] += i['est']
              #we add this to the 'used' list to keep track of what is already in the schedule
              used.append(i)
              #we mark this as 'checked'
              checked.append(i)
              #this is to restart the for loop, so that we can check if any of the tasks we checked earlier now fit the criteria
              break
            #if the item was not added to 'used', it is still checked
            checked.append(i)
          #if counter == len(others) it means every item in 'others' has been checked
          if counter == len(others):
            #so we stop the while loop since we cannot fit anything else into this slot, moving on to the next slot, and we break the for loop to save time
            done = True
            break
      #if time_left == 00:00 or you have no tasks left to use, we break the while loop to move on to the next slot and we break the for loop to save time
      else:
        done = True
    #time_left is always set to period[1] - period[0] at the start. It is possible therefore that time_left == 0 if period[0] > period[1]. This condition is for security.
    #And if time_left is not == Time(0,0), this means that even after attempting to fill up the slot we still have some free time, so we add that to the list 'fixed'
    if type(time_left) != int and time_left != Time(0,0):
      fixed.append({'start':period[0],'end':period[1],'name':'Free time'})
  #since some or all tasks from 'others' could have been added to 'fixed', and others remains unchanged throughout the whole for loop, we create a final_others list
  final_others = []
  #we check that if the task was not added to the schdule, we add it to final_others
  #this could be because it was too long or it was not important/urgent enough to be put into the schedule (ie. ['rank'] was too low)
  for i in others:
    if i not in used:
      final_others.append(i)
  #we sort fixed so that items are in order of when they happen
  #they may not be ordered because we simply appended items from 'others', from every slot
  #so you could have in 'fixed' an item starting at 0800 followed by one that occurs at 0700
  fixed = sorted(fixed, key = lambda i:i['start'])
  #we also sort final_others according to priority
  final_others = sorted(final_others, key = lambda i:i['rank'], reverse = 1)
  #return the final schedule (fixed) and the items that could not fit into the schedule (final_others)
  return [fixed, final_others]