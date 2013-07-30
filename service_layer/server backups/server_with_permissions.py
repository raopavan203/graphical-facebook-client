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
import urllib, json, score_calculation, fetch_fb_functions1, datetime

RECALCULATE_AFTER = 2628000 # Average Time Equivalent for a month in seconds

REQUIRED_PERMISSIONS = {'FRIENDS': ['basic_info'], 'PHOTOS': ['user_photos', 'friends_photos', 'user_likes', 'friends_likes', 'user_photo_video_tags'], 'CHECKINS': ['user_checkins', 'user_status', 'friends_status'], 'PROFILE': ['basic_info', 'user_birthday', 'user_education_history', 'user_interests', 'user_website', 'user_groups', 'user_hometown', 'user_email', 'user_religion_politics', 'user_about_me', 'user_activities', 'user_work_history', 'user_actions.news'], 'INBOX': ['read_mailbox'], 'FAMILY': ['user_relationships'], 'FEEDS AND LINKS': ['user_photos', 'user_likes', 'user_status', 'read_stream', 'friends_photos', 'friends_likes', 'friends_status'], 'STATUS': ['user_status', 'friends_status', 'user_likes', 'friends_likes']}
''' KEYS IN REQUIRED_PERMISSIONS:
	PHOTOS
	CHECKINS
	PROFILE
	INBOX
	FAMILY
	FEEDS AND LINKS
	STATUS
	FRIENDS
'''

app = Flask(__name__)

# DOCUMENTS

class Score(Document):
    friend_uid = StringField()
    score = FloatField()

class User(Document):
    uid = StringField()
    modified_time = ModifiedField()
    set_of_scores = ListField(DocumentField(Score), min_capacity=0, max_capacity=20)

# METHODS

session = Session.connect('fb')
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

# ROUTERS

@app.route('/_getProfile') 
def getProfile():
    accessToken = request.args.get('a', '', type=unicode)
    url = "https://graph.facebook.com/me?fields=id, name, gender, relationship_status, picture.height(200).width(200), link &access_token="+accessToken
    profile = json.loads(urllib.urlopen(url).read())
    print 'PROFILE: ',profile, type(profile)
    print profile['id']
    me=dict()
    for key in profile.keys():
        print "key: ", key
        if key=='picture':
            print profile[key]['data']
            me[key]=profile[key]['data']
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

    granted_permissions = fetch_fb_functions1.checkPermissions(accessToken)
    print '\n\npermissions\n\n', granted_permissions['data'][0]

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
              for list_elem in cur_user.set_of_scores:
                  profile = json.loads(fetch_fb_functions1.getProfile(accessToken, list_elem.friend_uid))
                  print 'PROFILE: ', profile
                  print type(profile)
                  print profile.keys()
                  print 'score: ',list_elem.score
        
                  if 'relationship_status' in profile.keys():
                      top_twenty.append({'id': list_elem.friend_uid, 'score': list_elem.score, 'name': profile['name'], 'gender': profile['gender'], 'relationship_status': profile['relationship_status'], 'link': profile['link'], 'picture': profile['picture']['data'] })
                  else:
                      top_twenty.append({'id': list_elem.friend_uid, 'score': list_elem.score, 'name': profile['name'], 'gender': profile['gender'], 'relationship_status': 'nill', 'link': profile['link'], 'picture': profile['picture']['data'] })

              print '****><><><>',top_twenty, type(top_twenty)
              session.end()
              return json.dumps(top_twenty)
          
    print '@@@@@@@@@@@@@@@@@    Calculating'

    fetch_string =  ''
    done_flag = 0
    if not set(REQUIRED_PERMISSIONS['PHOTOS']).isdisjoint(granted_permissions['data'][0].keys()):
        fetch_string = fetch_string + 'photos'
        done_flag = 1
    if not set(REQUIRED_PERMISSIONS['CHECKINS']).isdisjoint(granted_permissions['data'][0].keys()):
        if done_flag == 1:
            fetch_string = fetch_string + ', '
        fetch_string = fetch_string + 'checkins'
        done_flag = 1
    if not set(REQUIRED_PERMISSIONS['FEEDS AND LINKS']).isdisjoint(granted_permissions['data'][0].keys()):
        if done_flag == 1:
            fetch_string = fetch_string + ', '
        fetch_string = fetch_string + 'feed, links'
        done_flag =1
    if not set(REQUIRED_PERMISSIONS['FAMILY']).isdisjoint(granted_permissions['data'][0].keys()):           
        if done_flag == 1:
            fetch_string = fetch_string + ', '
        fetch_string = fetch_string + 'family'
        done_flag =1
    if not set(REQUIRED_PERMISSIONS['STATUS']).isdisjoint(granted_permissions['data'][0].keys()):
        if done_flag == 1:
            fetch_string = fetch_string + ', '
        fetch_string = fetch_string + 'statuses'
        done_flag =1
    if not set(REQUIRED_PERMISSIONS['INBOX']).isdisjoint(granted_permissions['data'][0].keys()):
        if done_flag == 1:
            fetch_string = fetch_string + ', '
        fetch_string = fetch_string + 'inbox.limit(500)'
        done_flag =1
        
    fetch_fb_functions1.getData(accessToken, uid, fetch_string)

    # if atleast one required in granted
    
    if not set(REQUIRED_PERMISSIONS['FRIENDS']).isdisjoint(granted_permissions['data'][0].keys()):
        print '\n\n  #### ##### atleast one FRIENDS\n\n'
        my_friends = fetch_fb_functions1.getFriends(accessToken)
        if 'friends' not in my_friends.keys():
           print 'no friends'
           return json.dumps('')
        #print 'my friends'
        #print my_friends
        score_calculation.init_scores(my_friends['friends']['data'])
    else:
        return json.dumps('')
        
    # if atleast one required in granted
    
    if not set(REQUIRED_PERMISSIONS['PHOTOS']).isdisjoint(granted_permissions['data'][0].keys()):
        print '\n\n  #### ##### atleast one PHOTOS\n\n'
        my_photos = fetch_fb_functions1.getPhotos(accessToken)
        if my_photos != None:
           print 'my_photos'
           #print my_photos
           print my_photos['tagged']
           score_calculation.update_scores(my_photos['tagged'], 3)
           print my_photos['liked by']
           score_calculation.update_scores(my_photos['liked by'], 2)
           print my_photos['commented by']
           score_calculation.update_scores(my_photos['commented by'], 2)

    # if atleast one required in granted
    
    if not set(REQUIRED_PERMISSIONS['CHECKINS']).isdisjoint(granted_permissions['data'][0].keys()):
        print '\n\n  #### ##### atleast one CHECKINS\n\n'
        my_checkins = fetch_fb_functions1.getCheckins(accessToken, uid) 
        print 'my_checkins'
        if my_checkins != None:
           print my_checkins['from']
           score_calculation.update_scores(my_checkins['from'], 4) 
        
           print my_checkins['tagged']
           score_calculation.update_scores(my_checkins['tagged'], 4) 

    # if atleast one required in granted
    
    if not set(REQUIRED_PERMISSIONS['FEEDS AND LINKS']).isdisjoint(granted_permissions['data'][0].keys()):  
        print '\n\n  #### ##### atleast one FEEDS AND LINKS\n\n'
        my_feeds = fetch_fb_functions1.getFeed(accessToken)
        if my_feeds != None:
            print 'my_feeds'
            print my_feeds['tagged']
            score_calculation.update_scores(my_feeds['tagged'], 3)
            print my_feeds['liked by']
            score_calculation.update_scores(my_feeds['liked by'], 2)
            print my_feeds['commented by']
            score_calculation.update_scores(my_feeds['commented by'], 2)
        my_links = fetch_fb_functions1.getLinks(accessToken)
        if my_links != None:
            print 'my_links'
            print my_links['tagged']
            score_calculation.update_scores(my_links['tagged'], 3)
            print my_links['liked by']
            score_calculation.update_scores(my_links['liked by'], 2)
            print my_links['commented by']
            score_calculation.update_scores(my_links['commented by'], 2)

    # if atleast one required in granted
    
    if not set(REQUIRED_PERMISSIONS['FAMILY']).isdisjoint(granted_permissions['data'][0].keys()):   
        print '\n\n  #### ##### atleast one FAMILY\n\n'
        my_family = fetch_fb_functions1.getFamily(accessToken)
        print 'my_family'
        if my_family != None:
           print my_family
           score_calculation.update_scores_family(my_family, 3)

    # if atleast one required in granted
    
    if not set(REQUIRED_PERMISSIONS['STATUS']).isdisjoint(granted_permissions['data'][0].keys()):  
        print '\n\n  #### ##### atleast one STATUS\n\n'
        my_status = fetch_fb_functions1.get_status(accessToken, uid)
        if my_status != None:
            print 'my_status'
            print my_status['tagged']
            score_calculation.update_scores(my_status['tagged'], 3)
            print my_status['liked by']
            score_calculation.update_scores(my_status['liked by'], 2)
            print my_status['commented by']
            score_calculation.update_scores(my_status['commented by'], 2)

    # if atleast one required in granted
    
    if not set(REQUIRED_PERMISSIONS['INBOX']).isdisjoint(granted_permissions['data'][0].keys()):  
        print '\n\n  #### ##### atleast one INBOX\n\n'
        my_inbox = fetch_fb_functions1.getInbox(accessToken, uid)
        if my_inbox != None:
           print 'my_inbox'
           print my_inbox
           score_calculation.update_scores_inbox(my_inbox, 3)

    sorted_score_list = score_calculation.show_scores()

    print '++++',sorted_score_list
    if len(sorted_score_list) >=20:
       top_twenty_friends = sorted_score_list[len(sorted_score_list)-20:]
    else:
       top_twenty_friends = sorted_score_list

    highest_index = len(top_twenty_friends)-1
    print '?????? $$$$$$', top_twenty_friends
    top_twenty = list()
       
    highest = top_twenty_friends[highest_index][1]
    print 'highest: ', highest

    my_friends_scores=list() # set of scores to be stored in DB

    for list_elem in top_twenty_friends:
        profile = json.loads(fetch_fb_functions1.getProfile(accessToken, list_elem[0]))
        print 'PROFILE: ', profile
        print type(profile)
        print profile.keys()
        print 'old score: ',list_elem[1]
        new_score = (list_elem[1]/highest)*100
        print'new score: ',new_score
        my_friends_scores.append(Score(friend_uid=list_elem[0], score=new_score))
        
        if 'relationship_status' in profile.keys():
            top_twenty.append({'id': list_elem[0], 'score': new_score, 'name': profile['name'], 'gender': profile['gender'], 'relationship_status': profile['relationship_status'], 'link': profile['link'], 'picture': profile['picture']['data'] })
        else:
            top_twenty.append({'id': list_elem[0], 'score': new_score, 'name': profile['name'], 'gender': profile['gender'], 'relationship_status': 'nill', 'link': profile['link'], 'picture': profile['picture']['data'] })

    store_user_record(uid, my_friends_scores, update_flag)

    print '****><><><>',top_twenty, type(top_twenty)
    session.end()
    return json.dumps(top_twenty)
    
@app.route('/')
def index():
    return render_template('tokenfetch.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0')
