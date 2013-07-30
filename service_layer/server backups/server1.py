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
from flaskext.mongoalchemy import MongoAlchemy
import urllib, json, score_calculation, fetch_fb_functions, datetime

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['MONGOALCHEMY_DATABASE'] = 'fb_close_friends'
db = MongoAlchemy(app)

# DOCUMENTS

class Score(db.Document):
    friend_uid = db.StringField()
    score = db.FloatField()

class User(db.Document):
    uid = db.StringField()
    modified_time = db.ModifiedField()
    set_of_scores = db.ListField(db.DocumentField(Score), min_capacity=0, max_capacity=20)

# METHODS

def store_user_record(my_uid, my_friends_scores):
    """
         Store Scores as <id>, <modified time>, <set of friends scores>
    """
    current_user = User(uid=my_uid, set_of_scores=my_friends_scores)
    current_user.save()

# ROUTERS

@app.route('/_getProfile') 
def getProfile():
    accessToken = request.args.get('a', '', type=unicode)
    url = "https://graph.facebook.com/me?fields=id, name, gender, relationship_status, picture.width(200), link &access_token="+accessToken
    profile = json.loads(urllib.urlopen(url).read())
    print profile, type(profile)
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

    print 'checking db'
    users = User.query.all()
    
    for cur_user in users:
       print cur_user.uid, cur_user.modified_time
       if cur_user.uid == uid:
          print datetime.datetime.now()
          time_diff = datetime.datetime.now()-cur_user.modified_time
          print 'time diff: ',time_diff.total_seconds()
          if time_diff.total_seconds() > 2628000:
              break    
          else:
              # fetch cur_user.set_of_scores
              print '##################   Fetching from DB'
              print cur_user.set_of_scores, type(cur_user.set_of_scores)
              top_twenty = list()
              for list_elem in cur_user.set_of_scores:
                  profile = json.loads(fetch_fb_functions.getProfile(accessToken, list_elem.friend_uid))
                  print 'PROFILE: ', profile
                  print type(profile)
                  print profile.keys()
                  print 'score: ',list_elem.score
        
                  if 'relationship_status' in profile.keys():
                      top_twenty.append({'id': list_elem.friend_uid, 'score': list_elem.score, 'name': profile['name'], 'gender': profile['gender'], 'relationship_status': profile['relationship_status'], 'link': profile['link'], 'picture': profile['picture']['data'] })
                  else:
                      top_twenty.append({'id': list_elem.friend_uid, 'score': list_elem.score, 'name': profile['name'], 'gender': profile['gender'], 'relationship_status': 'nill', 'link': profile['link'], 'picture': profile['picture']['data'] })

              print '****><><><>',top_twenty, type(top_twenty)
              return json.dumps(top_twenty)
          
    print '@@@@@@@@@@@@@@@@@    Calculating'
    my_friends = fetch_fb_functions.getFriends(accessToken)
    #print 'my_friends'
    #print my_friends['friends']['data']
    score_calculation.init_scores(my_friends['friends']['data'])

    my_photos = fetch_fb_functions.getPhotos(accessToken)
    print 'my_photos'
    #print my_photos
    print my_photos['tagged']
    score_calculation.update_scores(my_photos['tagged'], 3)
    print my_photos['liked by']
    score_calculation.update_scores(my_photos['liked by'], 2)
    print my_photos['commented by']
    score_calculation.update_scores(my_photos['commented by'], 2)

    my_checkins = fetch_fb_functions.getCheckins(accessToken, uid) 
    print 'my_checkins'
    if my_checkins != None:
       print my_checkins['from']
       score_calculation.update_scores(my_checkins['from'], 4) 
    
       print my_checkins['tagged']
       score_calculation.update_scores(my_checkins['tagged'], 4) 
    
    my_feeds = fetch_fb_functions.getFeed(accessToken)
    print 'my_feeds'
    print my_feeds['tagged']
    score_calculation.update_scores(my_feeds['tagged'], 3)
    print my_feeds['liked by']
    score_calculation.update_scores(my_feeds['liked by'], 2)
    print my_feeds['commented by']
    score_calculation.update_scores(my_feeds['commented by'], 2)
  
    my_family = fetch_fb_functions.getFamily(accessToken)
    print 'my_family'
    if my_family != None:
       print my_family
       score_calculation.update_scores_family(my_family, 3)

    my_status = fetch_fb_functions.get_status(accessToken, uid)
    print 'my_status'
    print my_status['tagged']
    score_calculation.update_scores(my_status['tagged'], 3)
    print my_status['liked by']
    score_calculation.update_scores(my_status['liked by'], 2)
    print my_status['commented by']
    score_calculation.update_scores(my_status['commented by'], 2)
    
    my_links = fetch_fb_functions.getLinks(accessToken)
    print 'my_links'
    print my_links['tagged']
    score_calculation.update_scores(my_links['tagged'], 3)
    print my_links['liked by']
    score_calculation.update_scores(my_links['liked by'], 2)
    print my_links['commented by']
    score_calculation.update_scores(my_links['commented by'], 2)

    my_inbox = fetch_fb_functions.getInbox(accessToken, uid)
    print 'my_inbox'
    print my_inbox
    score_calculation.update_scores_inbox(my_inbox, 3)
    sorted_score_list = score_calculation.show_scores()
    print '++++',sorted_score_list
    top_twenty_friends = sorted_score_list[len(sorted_score_list)-20:]
    
    print '?????? $$$$$$', top_twenty_friends
    top_twenty = list()

    highest = top_twenty_friends[19][1]
    print 'highest: ', highest

    my_friends_scores=list() # set of scores to be stored in DB

    for list_elem in top_twenty_friends:
        profile = json.loads(fetch_fb_functions.getProfile(accessToken, list_elem[0]))
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

    store_user_record(uid, my_friends_scores)

    print '****><><><>',top_twenty, type(top_twenty)
    return json.dumps(top_twenty)
    
@app.route('/')
def index():
    return render_template('tokenfetch.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0')
