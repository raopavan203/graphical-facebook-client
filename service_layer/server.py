# -*- coding: utf-8 -*-
"""
jQuery Example
~~~~~~~~~~~~~~

A simple application that shows how Flask and jQuery get along.

:copyright: (c) 2010 by Armin Ronacher.
:license: BSD, see LICENSE for more details.
"""
from flask import Flask, jsonify, render_template, request, redirect, url_for, session

import urllib, json, score_calculation, fetch_fb_functions

app = Flask(__name__)

@app.route('/_getProfile') 
def getProfile():
    accessToken = request.args.get('a', '', type=unicode)
    url = "https://graph.facebook.com/me?fields=id, name, gender, relationship_status, picture, link &access_token="+accessToken
    data = urllib.urlopen(url).read()
    print data
    return data

@app.route('/_getCloseFriends')
def getCloseFriends():
    accessToken = request.args.get('a', '', type=unicode)
    uid = request.args.get('b', '', type=unicode)
    print 'uid='+uid
    print 'in get close friends'
    my_friends = fetch_fb_functions.getFriends(accessToken)
    #print 'my_friends'
    #print my_friends['friends']['data']
    score_calculation.init_scores(my_friends['friends']['data'])

    my_photos = fetch_fb_functions.getPhotos(accessToken)
    print 'my_photos'
    #print my_photos
    print my_photos['tagged']
    score_calculation.update_scores(my_photos['tagged'], 75)
    print my_photos['liked by']
    score_calculation.update_scores(my_photos['liked by'], 35)
    print my_photos['commented by']
    score_calculation.update_scores(my_photos['commented by'], 35)

    my_checkins = fetch_fb_functions.getCheckins(accessToken, uid) 
    print 'my_checkins'
    if my_checkins != None:
       print my_checkins['from']
       score_calculation.update_scores(my_checkins['from'], 100) 
    
       print my_checkins['tagged']
       score_calculation.update_scores(my_checkins['tagged'], 100) 
    
    my_feeds = fetch_fb_functions.getFeed(accessToken)
    print 'my_feeds'
    print my_feeds['tagged']
    score_calculation.update_scores(my_feeds['tagged'], 75)
    print my_feeds['liked by']
    score_calculation.update_scores(my_feeds['liked by'], 35)
    print my_feeds['commented by']
    score_calculation.update_scores(my_feeds['commented by'], 35)
  
    my_family = fetch_fb_functions.getFamily(accessToken)
    print 'my_family'
    if my_family != None:
       print my_family
       score_calculation.update_scores_family(my_family, 75)

    my_status = fetch_fb_functions.get_status(accessToken, uid)
    print 'my_status'
    print my_status['tagged']
    score_calculation.update_scores(my_status['tagged'], 75)
    print my_status['liked by']
    score_calculation.update_scores(my_status['liked by'], 35)
    print my_status['commented by']
    score_calculation.update_scores(my_status['commented by'], 35)
    
    my_links = fetch_fb_functions.getLinks(accessToken)
    print 'my_links'
    print my_links['tagged']
    score_calculation.update_scores(my_links['tagged'], 75)
    print my_links['liked by']
    score_calculation.update_scores(my_links['liked by'], 35)
    print my_links['commented by']
    score_calculation.update_scores(my_links['commented by'], 35)

    my_inbox = fetch_fb_functions.getInbox(accessToken, uid)
    print 'my_inbox'
    print my_inbox
    score_calculation.update_scores_inbox(my_inbox, 75)
    sorted_score_list = score_calculation.show_scores()
    print '++++',sorted_score_list
    top_twenty_friends = sorted_score_list[len(sorted_score_list)-20:]
    
    print '????', top_twenty_friends
    top_twenty = list()
    for list_elem in top_twenty_friends:
        profile = json.loads(fetch_fb_functions.getProfile(accessToken, list_elem[0]))
        print 'PROFILE: ', profile
        print type(profile)
        print profile.keys()
        if 'relationship_status' in profile.keys():
            top_twenty.append({'id': list_elem[0], 'score': list_elem[1], 'name': profile['name'], 'gender': profile['gender'], 'relationship_status': profile['relationship_status'], 'link': profile['link'], 'picture': profile['picture'] })
        else:
            top_twenty.append({'id': list_elem[0], 'score': list_elem[1], 'name': profile['name'], 'gender': profile['gender'], 'relationship_status': 'nill', 'link': profile['link'], 'picture': profile['picture'] })
    print '****><><><>',top_twenty
    return jsonify(top_twenty)
    
@app.route('/')
def index():
    return render_template('tokenfetch.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0')
