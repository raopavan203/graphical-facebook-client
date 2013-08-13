"""
Flask Server for Graphical Facebook Client

1) Listens to Client for serving requested Facebook-data
2) Calls Facebook Graph API to fetch Facebook-data
3) Calculates scores for all friends in user's friendlist based on:
   a) Inbox History
   b) Tags in Posts, Photos, Checkins, Statuses, Links
   c) Likes and Comments in Posts, Photos, Checkins, Statuses, Links
4) Returns Profiles of Top Twenty Friends (closest friends) to client
5) Stores the scores of top twenty friends in MongoDB
6) Fetches scores from MongoDB in subsequent requests
7) Updates scores after a month's time span

This file contains the Server support functions

1) Calculate Scores and evaluate Closest Friends
2) Fetch Closest From DB
3) Store Closest in DB

"""

# INITIALIZATIONS

from __future__ import division
from flask import Flask, jsonify, request
import urllib, json, datetime, time
import score_calculation1, fetch_fb_functions1, db_functions1, weights
from threading import Thread
from Queue import Queue

concurrent = 20

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

# METHODS

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
    print 'GET PROFILE THREAD'

    if 'statuses' in profile.keys():
       recent_status={}
       if 'data' in profile['statuses'].keys():
           if 'updated_time' in profile['statuses']['data'][0].keys():
               recent_status['updated_time'] = profile['statuses']['data'][0]['updated_time']
           if 'message' in profile['statuses']['data'][0].keys():
               recent_status['message'] = profile['statuses']['data'][0]['message']     

           if 'relationship_status' in profile.keys():
               current_profile = {'id': uid, 
                                  'score': score, 
                                  'name': profile['name'], 
                                  'gender': profile['gender'], 
                                  'relationship_status': profile['relationship_status'], 
                                  'link': profile['link'], 
                                  'picture': profile['picture']['data'], 'status': recent_status}
           else:
               current_profile = {'id': uid, 
                                  'score': score, 
                                  'name': profile['name'], 
                                  'gender': profile['gender'], 
                                  'link': profile['link'], 
                                  'picture': profile['picture']['data'], 
                                  'status': recent_status}
    else:
       if 'relationship_status' in profile.keys():
          current_profile = {'id': uid, 
                             'score': score, 
                             'name': profile['name'], 
                             'gender': profile['gender'], 
                             'relationship_status': profile['relationship_status'], 
                             'link': profile['link'], 
                             'picture': profile['picture']['data']}
       else:
          current_profile = {'id': uid, 
                             'score': score, 
                             'name': profile['name'], 
                             'gender': profile['gender'], 
                             'relationship_status': 'nill', 
                             'link': profile['link'], 
                             'picture': profile['picture']['data'] }

    return current_profile 

def fetchClosestProfiles(top_twenty_friends, update_flag, uid, accessToken):
    highest_index = len(top_twenty_friends)-1       
    highest = top_twenty_friends[highest_index][1]
    top_twenty = list() # returned to front end  
    my_friends_scores=list() # set of scores to be stored in DB

    try:
       t=[] # list of threads
       for list_elem in top_twenty_friends:
          url = "https://graph.facebook.com/" + list_elem[0] + "?fields=id, name, \
gender, relationship_status, picture.height(200).width(200), link, \
statuses.limit(1).fields(message,updated_time) &access_token=" + accessToken
          new_score = (list_elem[1]/highest)*100
          temp = ThreadWithReturnValue(target=doWork, 
                                       args=(list_elem[0], url.strip(), new_score))   
                  # pass tuple(uid, url, new_score, top_twenty) in thread   
          temp.daemon=True
          temp.start()
          t.append(temp)
          my_friends_scores.append(db_functions1.Score(friend_uid=list_elem[0], 
                                   score=new_score))
       for thread_index in range(0,len(t)):
          current_profile = t[thread_index].join()
          print '\n\nWhile Joining: ', current_profile
          top_twenty.append(current_profile)
    except KeyboardInterrupt:
       sys.exit(1)

    db_functions1.store_user_record(uid, my_friends_scores, update_flag)
    db_functions1.session.end()
    
    print top_twenty
    return top_twenty

def fetchClosestFromDB(my_data_handler, cur_user):
    # fetch cur_user.set_of_scores
    print 'Fetching from DB'
    top_twenty = list()

    try:
       t=[] # list of threads
       for list_elem in cur_user.set_of_scores:
          url = "https://graph.facebook.com/" + list_elem.friend_uid + "?fields=id, name, \
gender, relationship_status, picture.height(200).width(200), link, \
statuses.limit(1).fields(message,updated_time) &access_token=" + my_data_handler.accessToken
          temp = ThreadWithReturnValue(target=doWork, 
                                       args=(list_elem.friend_uid, url.strip(), list_elem.score))  
                           # pass tuple(uid, url, new_score) in thread   
          temp.daemon=True
          temp.start()
          t.append(temp)
       for thread_index in range(0,len(t)):
          current_profile = t[thread_index].join()
          print '\n\nWhile Joining: ', current_profile
          top_twenty.append(current_profile)
    except KeyboardInterrupt:
       sys.exit(1)
    print top_twenty
    db_functions1.session.end()
    return top_twenty

def processFriendLists(all_data, my_data_handler, my_scores):
    my_friendlists = my_data_handler.getFriendLists(all_data)
    if my_friendlists != None:
       print 'my_friendlists'
       my_scores.update_scores_friendlist(my_friendlists['close_friends'], 
                                          weights.set_of_weights['close_friends'])
       my_scores.update_scores_friendlist(my_friendlists['work'], 
                                          weights.set_of_weights['work'])
       my_scores.update_scores_friendlist(my_friendlists['education'], 
                                          weights.set_of_weights['education'])
       my_scores.update_scores_friendlist(my_friendlists['user_created'], 
                                          weights.set_of_weights['user_created'])
       my_scores.update_scores_friendlist(my_friendlists['current_city'], 
                                          weights.set_of_weights['current_city'])

def processPicsByMe(pics_by_me, my_data_handler, my_scores, uid):
    if pics_by_me != None:
       few_tags_pics_by_me = []
       many_tags_pics_by_me = []       
       my_data_handler.splitPhotosByTagCount(pics_by_me, 
                                             few_tags_pics_by_me, 
                                             many_tags_pics_by_me)

       by_me_photos = my_data_handler.getPhotos(pics_by_me, 
                                                few_tags_pics_by_me, 
                                                uid)
       print 'by_me_photos'
       my_scores.update_scores(by_me_photos['tagged'], 
                               weights.set_of_weights['pics_with_few_tags_by_me_tagged'])
       my_scores.update_scores(by_me_photos['liked by'], 
                               weights.set_of_weights['pics_with_few_tags_by_me_liked by'])
       my_scores.update_scores(by_me_photos['commented by'], 
                               weights.set_of_weights['pics_with_few_tags_by_me_commented by'])

       by_me_photos = my_data_handler.getPhotos(pics_by_me, many_tags_pics_by_me, uid)
       my_scores.update_scores(by_me_photos['tagged'], 
                               weights.set_of_weights['pics_with_many_tags_by_me_tagged'])
       my_scores.update_scores(by_me_photos['liked by'], 
                               weights.set_of_weights['pics_with_many_tags_by_me_liked by'])
       my_scores.update_scores(by_me_photos['commented by'], 
                               weights.set_of_weights['pics_with_many_tags_by_me_commented by'])

def processPicsByOthers(pics_by_others, my_data_handler, my_scores, uid):
    if pics_by_others != None:
       few_tags_pics_by_others = []
       many_tags_pics_by_others = []       
       my_data_handler.splitPhotosByTagCount(pics_by_others, 
                                             few_tags_pics_by_others, 
                                             many_tags_pics_by_others)

       by_others_photos = my_data_handler.getPhotos(pics_by_others, 
                                                    few_tags_pics_by_others, 
                                                    uid)
       print 'by_others_photos'
       my_scores.update_scores(by_others_photos['tagged'], 
                               weights.set_of_weights['pics_with_few_tags_by_others_tagged'])
       my_scores.update_scores(by_others_photos['liked by'], 
                               weights.set_of_weights['pics_with_few_tags_by_others_liked by'])
       my_scores.update_scores(by_others_photos['commented by'], 
                               weights.set_of_weights['pics_with_few_tags_by_others_commented by'])

       by_others_photos = my_data_handler.getPhotos(pics_by_others, 
                                                    many_tags_pics_by_others, 
                                                    uid)
       my_scores.update_scores(by_others_photos['tagged'], 
                               weights.set_of_weights['pics_with_many_tags_by_others_tagged'])
       my_scores.update_scores(by_others_photos['liked by'], 
                               weights.set_of_weights['pics_with_many_tags_by_others_liked by'])
       my_scores.update_scores(by_others_photos['commented by'], 
                               weights.set_of_weights['pics_with_many_tags_by_others_commented by'])

def processCheckins(all_data, uid, my_data_handler, my_scores):
    my_checkins = my_data_handler.getCheckins(uid, all_data) 
    print 'my_checkins'
    if my_checkins != None:
       my_scores.update_scores(my_checkins['from'], 
                               weights.set_of_weights['checkins_from']) 
       my_scores.update_scores(my_checkins['tagged'], 
                               weights.set_of_weights['checkins_tagged']) 

def processFeedByMe(feed_by_me, my_data_handler, my_scores):
    if feed_by_me != None:
       my_feeds = my_data_handler.getFeed(feed_by_me)
       print 'feeds_by_me'
       my_scores.update_scores(my_feeds['tagged'], 
                               weights.set_of_weights['feeds_by_me_tagged'])
       my_scores.update_scores(my_feeds['liked by'], 
                               weights.set_of_weights['feeds_by_me_liked by'])
       my_scores.update_scores(my_feeds['commented by'],  
                               weights.set_of_weights['feeds_by_me_commented by'])

def processFeedByOthers(feed_by_others, my_data_handler, my_scores):
    if feed_by_others != None:
       others_feeds = my_data_handler.getFeed(feed_by_others)
       print 'feeds_by_others'
       my_scores.update_scores(others_feeds['tagged'], 
                               weights.set_of_weights['feeds_by_others_tagged'])
       my_scores.update_scores(others_feeds['liked by'], 
                               weights.set_of_weights['feeds_by_others_liked by'])
       my_scores.update_scores(others_feeds['commented by'], 
                               weights.set_of_weights['feeds_by_others_commented by'])
    
def processFamily(all_data, my_data_handler, my_scores):
    my_family = my_data_handler.getFamily(all_data)
    print 'my_family'
    if my_family != None:
       my_scores.update_scores_family(my_family, weights.set_of_weights['family'])

def processStatus(uid, all_data, my_data_handler, my_scores):
    my_status = my_data_handler.get_status(uid, all_data)
    if my_status != None:
       print 'my_status'
       my_scores.update_scores(my_status['tagged'], 
                               weights.set_of_weights['status_tagged'])
       my_scores.update_scores(my_status['liked by'], 
                               weights.set_of_weights['status_liked by'])
       my_scores.update_scores(my_status['commented by'], 
                               weights.set_of_weights['status_commented by'])

def processLinks(all_data, my_data_handler, my_scores):
    my_links = my_data_handler.getLinks(all_data)
    if my_links != None:
       print 'my_links'
       my_scores.update_scores(my_links['tagged'], 
                               weights.set_of_weights['links_tagged'])
       my_scores.update_scores(my_links['liked by'], 
                               weights.set_of_weights['links_liked by'])
       my_scores.update_scores(my_links['commented by'], 
                               weights.set_of_weights['links_commented by'])

def processInbox(uid, all_data, my_data_handler, my_scores):
    my_inbox = my_data_handler.getInbox(uid, all_data)
    if my_inbox != None:
       print 'my_inbox'
       my_scores.update_scores_inbox(my_inbox, weights.set_of_weights['inbox'])

def calculateClosest(my_data_handler, uid, update_flag):
    print 'Calculating'
    my_friends = my_data_handler.getFriends()
    if 'friends' not in my_friends.keys():
        print 'no friends'
        return json.dumps('')
    
    friend_list = my_friends['friends']['data']
    my_scores = score_calculation1.Scores(friend_list)

    fetch_string = 'photos, checkins, feed, links, family, inbox.limit(500), \
statuses, friendlists.fields(members,list_type)' 
    all_data = my_data_handler.getData(uid, fetch_string)

    processFriendLists(all_data, my_data_handler, my_scores)

    pics_by_me = []
    pics_by_others = []
    split_pics = my_data_handler.splitPhotos(all_data, 
                                             uid, 
                                             pics_by_me, 
                                             pics_by_others)
    processPicsByMe(pics_by_me, my_data_handler, my_scores, uid) 
    processPicsByOthers(pics_by_others, my_data_handler, my_scores, uid)

    processCheckins(all_data, uid, my_data_handler, my_scores)

    feed_by_me = []
    feed_by_others = []
    split_feed = my_data_handler.splitFeed(all_data, uid, feed_by_me, feed_by_others)   

    processFeedByMe(feed_by_me, my_data_handler, my_scores)
    processFeedByMe(feed_by_others, my_data_handler, my_scores)
     
    processFamily(all_data, my_data_handler, my_scores)

    processStatus(uid, all_data, my_data_handler, my_scores)
    processLinks(all_data, my_data_handler, my_scores)
    processInbox(uid, all_data, my_data_handler, my_scores)
 
    sorted_score_list = my_scores.show_scores()

    print 'SORTED SCORE LIST: ', sorted_score_list
    if len(sorted_score_list) >=20:
       top_twenty_friends = sorted_score_list[len(sorted_score_list)-20:]
    else:
       top_twenty_friends = sorted_score_list
    top_twenty = fetchClosestProfiles(top_twenty_friends, 
                                      update_flag, 
                                      uid, 
                                      my_data_handler.accessToken)
    return top_twenty

