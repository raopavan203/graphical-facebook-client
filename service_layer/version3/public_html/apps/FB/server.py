# RECENT CHANGES HERE

# -*- coding: utf-8 -*-
"""
jQuery Example
~~~~~~~~~~~~~~

A simple application that shows how Flask and jQuery get along.

:copyright: (c) 2010 by Armin Ronacher.
:license: BSD, see LICENSE for more details.
"""

# INIT

from __future__ import division
from flask import Flask, jsonify, render_template, request, redirect, url_for, session
from mongoalchemy.document import Document
from mongoalchemy.fields import *
from mongoalchemy.session import Session
import urllib, json, score_calculation, fetch_fb_functions, datetime
from threading import Thread
from Queue import Queue
import time

RECALCULATE_AFTER = 2628000 # Average Time Equivalent for a month in seconds
concurrent = 20

app = Flask(__name__)

class ThreadWithReturnValue(Thread):
    def __init__(self, group=None, target=None, name=None,
                 args=(), kwargs={}, Verbose=None):
        Thread.__init__(self, group, target, name, args, kwargs, Verbose)
        self._return = None
    def run(self):
        if self._Thread__target is not None:
            self._return = self._Thread__target(*self._Thread__args,
                                                **self._Thread__kwargs)
    def join(self):
        Thread.join(self)
        return self._return

# DOCUMENTS

class Score(Document):
    friend_uid = StringField()
    score = FloatField()

class User(Document):
    uid = StringField()
    modified_time = ModifiedField()
    set_of_scores = ListField(DocumentField(Score), min_capacity=0, max_capacity=20)

# METHODS

session = Session.connect('fb-closest-friends')
#session.clear_collection(User)

def store_user_record(my_uid, my_friends_scores, update_flag):
    """
         Store Scores as <id>, <modified time>, <set of friends scores>
    """

    print 'Update Flag = ', update_flag
    if update_flag == 1:
        current_user = session.query(User)
        current_user.set(User.set_of_scores, my_friends_scores).execute()
        print '%%%%%%% Update Success'
    else:
        current_user = User(uid=my_uid, set_of_scores=my_friends_scores)
        session.insert(current_user)
        print '$$$$$$$$ Insert Success'

def doWork(uid, url, score):
    while True:
        print '\nCurrent Tuple: ', uid, url, score
        data, url=getData(url)
        current_profile = doSomethingWithResult(data, uid, score)
        return current_profile

def getData(ourl):
    try:
        data = json.loads(urllib.urlopen(ourl).read())
        return data, ourl
    except:
        return "error", ourl

def doSomethingWithResult(profile, uid, score):

    print 'PROFILE: ', profile
    print type(profile)
    print profile.keys()

    if 'statuses' in profile.keys():
       recent_status={}
       if 'data' in profile['statuses'].keys():
           if 'updated_time' in profile['statuses']['data'][0].keys():
               print '^^^^^^ &&&&&&& ', profile['statuses']['data'][0]['updated_time']
               recent_status['updated_time'] = profile['statuses']['data'][0]['updated_time']
           if 'message' in profile['statuses']['data'][0].keys():
               #print '^^^^^^ &&&&&&& ', profile['statuses']['data'][0]['message']
               print  '^^^^^^ ', profile['statuses']['data'][0], type(profile['statuses']['data'][0]) 
               recent_status['message'] = profile['statuses']['data'][0]['message']     
           print '/n/n **** RECENT ', recent_status

           if 'relationship_status' in profile.keys():
               current_profile = {'id': uid, 'score': score, 'name': profile['name'], 'gender': profile['gender'], 'relationship_status': profile['relationship_status'], 'link': profile['link'], 'picture': profile['picture']['data'], 'status': recent_status}
           else:
               current_profile = {'id': uid, 'score': score, 'name': profile['name'], 'gender': profile['gender'], 'link': profile['link'], 'picture': profile['picture']['data'], 'status': recent_status}
    else:
       if 'relationship_status' in profile.keys():
          current_profile = {'id': uid, 'score': score, 'name': profile['name'], 'gender': profile['gender'], 'relationship_status': profile['relationship_status'], 'link': profile['link'], 'picture': profile['picture']['data']}
       else:
          current_profile = {'id': uid, 'score': score, 'name': profile['name'], 'gender': profile['gender'], 'relationship_status': 'nill', 'link': profile['link'], 'picture': profile['picture']['data'] }

    return current_profile 

# ROUTERS

@app.route('/_getData')
def getAnyData():
    accessToken = request.args.get('a', '', type=unicode)
    uid = request.args.get('b', '', type=unicode)
    fetch_string = request.args.get('c', '', type=unicode)
    data = fetch_fb_functions.getData(accessToken, uid, fetch_string)
    return json.dumps(data)

@app.route('/_getProfile') 
def getProfile():
    accessToken = request.args.get('a', '', type=unicode)
    url = "https://graph.facebook.com/me?fields=id, name, gender, relationship_status, picture.height(200).width(200), link, statuses.limit(1).fields(message,updated_time) &access_token="+accessToken
    profile = json.loads(urllib.urlopen(url).read())
    print 'PROFILE: ',profile, type(profile)
    print profile['id']
    me=dict()
    for key in profile.keys():
        print "key: ", key
        if key=='picture':
            print profile[key]['data']
            me[key]=profile[key]['data']
        elif key == 'statuses':
            recent_status={}
            recent_status['updated_time'] = profile['statuses']['data'][0]['updated_time']
            recent_status['message'] = profile['statuses']['data'][0]['message']
            me['status'] = recent_status
            print me['status']
        else:
            print profile[key]
            me[key]=profile[key]
    print json.dumps(me)
    return json.dumps(me)

@app.route('/_getCloseFriends')
def getCloseFriends():
    accessToken = request.args.get('a', '', type=unicode)
    uid = request.args.get('b', '', type=unicode)
    print 'uid='+uid
    print 'in get close friends'

    print 'checking db'
    update_flag = 0

    users = session.query(User)
    
    for cur_user in users:
       print cur_user.uid, cur_user.modified_time
       if cur_user.uid == uid:
          print datetime.datetime.now()
          time_diff = datetime.datetime.now()-cur_user.modified_time
          print 'time diff: ',time_diff.total_seconds()
          if time_diff.total_seconds() > 2628000:
              update_flag = 1
              break    
          else:
              # fetch cur_user.set_of_scores
              print '##################   Fetching from DB'
              print cur_user.set_of_scores, type(cur_user.set_of_scores)
              top_twenty = list()

              start_time = time.time()
              try:
                 t=[] # list of threads
                 for list_elem in cur_user.set_of_scores:
                     url = "https://graph.facebook.com/" + list_elem.friend_uid + "?fields=id, name, gender, relationship_status, picture.height(200).width(200), link, statuses.limit(1).fields(message,updated_time) &access_token="+accessToken
                     print 'score: ',list_elem.score
                     temp = ThreadWithReturnValue(target=doWork, args=(list_elem.friend_uid, url.strip(), list_elem.score))   # pass tuple(uid, url, new_score) in thread   
                     temp.daemon=True
                     temp.start()
                     t.append(temp)
                 for thread_index in range(0,len(t)):
                     current_profile = t[thread_index].join()
                     print '\n\nWhile Joining: ', current_profile
                     top_twenty.append(current_profile)
              except KeyboardInterrupt:
                 sys.exit(1)
              print time.time() - start_time, "seconds"


              print '****><><><>',top_twenty, type(top_twenty)
              session.end()
              return json.dumps(top_twenty)
          
    print '@@@@@@@@@@@@@@@@@    Calculating'
    my_friends = fetch_fb_functions.getFriends(accessToken)
    if 'friends' not in my_friends.keys():
        print 'no friends'
        return json.dumps('')
    
    #print 'my friends'
    #print my_friends

    score_list = {}
    sorted_score_list = {}
      
    friend_list = my_friends['friends']['data']
    print 'init_scores'
    for current_friend in friend_list:
        score_list[current_friend['id']] = 1
    #print score_list

    fetch_string = 'photos, checkins, feed, links, family, inbox.limit(500), statuses' 
    all_data = fetch_fb_functions.getData(accessToken, uid, fetch_string)

    my_photos = fetch_fb_functions.getPhotos(accessToken, all_data)
    if my_photos != None:
       print 'my_photos'
       #print my_photos
       print my_photos['tagged']
       score_calculation.update_scores(my_photos['tagged'], 3, score_list)
       print my_photos['liked by']
       score_calculation.update_scores(my_photos['liked by'], 2, score_list)
       print my_photos['commented by']
       score_calculation.update_scores(my_photos['commented by'], 2, score_list)

    my_checkins = fetch_fb_functions.getCheckins(accessToken, uid, all_data) 
    print 'my_checkins'
    if my_checkins != None:
       print my_checkins['from']
       score_calculation.update_scores(my_checkins['from'], 4, score_list) 
    
       print my_checkins['tagged']
       score_calculation.update_scores(my_checkins['tagged'], 4, score_list) 
    
    my_feeds = fetch_fb_functions.getFeed(accessToken, all_data)
    if my_feeds != None:
       print 'my_feeds'
       print my_feeds['tagged']
       score_calculation.update_scores(my_feeds['tagged'], 3, score_list)
       print my_feeds['liked by']
       score_calculation.update_scores(my_feeds['liked by'], 2, score_list)
       print my_feeds['commented by']
       score_calculation.update_scores(my_feeds['commented by'], 2, score_list)
    
    my_family = fetch_fb_functions.getFamily(accessToken, all_data)
    print 'my_family'
    if my_family != None:
       print my_family
       score_calculation.update_scores_family(my_family, 3, score_list)

    my_status = fetch_fb_functions.get_status(accessToken, uid, all_data)
    if my_status != None:
       print 'my_status'
       print my_status['tagged']
       score_calculation.update_scores(my_status['tagged'], 3, score_list)
       print my_status['liked by']
       score_calculation.update_scores(my_status['liked by'], 2, score_list)
       print my_status['commented by']
       score_calculation.update_scores(my_status['commented by'], 2, score_list)

    my_links = fetch_fb_functions.getLinks(accessToken, all_data)
    if my_links != None:
       print 'my_links'
       print my_links['tagged']
       score_calculation.update_scores(my_links['tagged'], 3, score_list)
       print my_links['liked by']
       score_calculation.update_scores(my_links['liked by'], 2, score_list)
       print my_links['commented by']
       score_calculation.update_scores(my_links['commented by'], 2, score_list)

    my_inbox = fetch_fb_functions.getInbox(accessToken, uid, all_data)
    if my_inbox != None:
       print 'my_inbox'
       print my_inbox
       score_calculation.update_scores_inbox(my_inbox, 3, score_list)

    sorted_score_list = score_calculation.show_scores(score_list)

    print '++++',sorted_score_list
    if len(sorted_score_list) >=20:
       top_twenty_friends = sorted_score_list[len(sorted_score_list)-20:]
    else:
       top_twenty_friends = sorted_score_list

    highest_index = len(top_twenty_friends)-1
    print '?????? $$$$$$', top_twenty_friends
    
       
    highest = top_twenty_friends[highest_index][1]
    print 'highest: ', highest

    top_twenty = list() # returned to front end  
    my_friends_scores=list() # set of scores to be stored in DB

    start_time = time.time()
    try:
       t=[] # list of threads
       for list_elem in top_twenty_friends:
          url = "https://graph.facebook.com/" + list_elem[0] + "?fields=id, name, gender, relationship_status, picture.height(200).width(200), link, statuses.limit(1).fields(message,updated_time) &access_token="+accessToken
          print 'old score: ',list_elem[1]
          new_score = (list_elem[1]/highest)*100
          print'new score: ',new_score
          temp = ThreadWithReturnValue(target=doWork, args=(list_elem[0], url.strip(), new_score))   # pass tuple(uid, url, new_score, top_twenty) in thread   
          temp.daemon=True
          temp.start()
          t.append(temp)
          my_friends_scores.append(Score(friend_uid=list_elem[0], score=new_score))
       for thread_index in range(0,len(t)):
          current_profile = t[thread_index].join()
          print '\n\nWhile Joining: ', current_profile
          top_twenty.append(current_profile)
    except KeyboardInterrupt:
       sys.exit(1)
    print time.time() - start_time, "seconds"

    store_user_record(uid, my_friends_scores, update_flag)
    session.end()
    
    print '****><><><>',top_twenty, type(top_twenty)
    return json.dumps(top_twenty)
    
@app.route('/')
def index():
    return render_template('tokenfetch.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug = True)
