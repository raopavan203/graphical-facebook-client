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
 
This File Contains the APIs exposed to front end:
1) _getProfile
2) _getCloseFriends
3) _getData

"""

# INITIALIZATIONS

from flask import Flask, render_template, request, url_for
import json, urllib, datetime
import server_support_functions1, fetch_fb_functions1, db_functions1

RECALCULATE_AFTER = 2628000 # Average Time Equivalent for a month in seconds
app = Flask(__name__)

# ROUTERS

@app.route('/_getData')
def getAnyData():
    accessToken = request.args.get('a', '', type=unicode)
    uid = request.args.get('b', '', type=unicode)
    fetch_string = request.args.get('c', '', type=unicode)
    data = my_data_handler.getData(accessToken, uid, fetch_string)
    return json.dumps(data)

@app.route('/_getProfile') 
def getProfile():
    print 'GET PROFILE'
    accessToken = request.args.get('a', '', type=unicode)

    url = "https://graph.facebook.com/me?fields=id, name, gender, \
relationship_status, picture.height(200).width(200), link, \
statuses.limit(1).fields(message,updated_time) &access_token=" + accessToken

    profile = json.loads(urllib.urlopen(url).read())
    me=dict()
    for key in profile.keys():
        if key=='picture':
            me[key]=profile[key]['data']
        elif key == 'statuses':
            recent_status={}
            if 'updated_time' in profile['statuses']['data'][0].keys():
                recent_status['updated_time'] = profile['statuses']['data'][0]['updated_time']
            if 'message' in profile['statuses']['data'][0].keys():
                recent_status['message'] = profile['statuses']['data'][0]['message']
            else:
                recent_status['message'] = 'Status Without Message'
            me['status'] = recent_status
        else:
            me[key]=profile[key]
    return json.dumps(me)

@app.route('/_getCloseFriends')
def getCloseFriends():
    print 'GET CLOSE FRIENDS'
    accessToken = request.args.get('a', '', type=unicode)
    uid = request.args.get('b', '', type=unicode)
    my_data_handler = fetch_fb_functions1.FacebookDataHandler(accessToken)

    print 'checking db'
    update_flag = 0

    users = db_functions1.session.query(db_functions1.User)
    
    for cur_user in users:
       print cur_user.uid, cur_user.modified_time
       if cur_user.uid == uid:
          time_diff = datetime.datetime.now()-cur_user.modified_time
          if time_diff.total_seconds() > RECALCULATE_AFTER:
              update_flag = 1
              top_twenty = server_support_functions1.calculateClosest(my_data_handler,
                                                                      uid, 
                                                                      update_flag)  
              return json.dumps(top_twenty)    
          else:
              top_twenty = server_support_functions1.fetchClosestFromDB(my_data_handler,
                                                                       cur_user)
              return json.dumps(top_twenty)

    top_twenty = server_support_functions1.calculateClosest(my_data_handler,
                                                            uid, 
                                                            update_flag)  
    return json.dumps(top_twenty)
    
@app.route('/')
def index():
    return render_template('tokenfetch.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug = True)
