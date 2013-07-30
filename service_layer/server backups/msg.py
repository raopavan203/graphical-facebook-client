from flask import Flask, redirect, url_for, session, request
from flask_oauth import OAuth
from collections import Counter

import urllib, json

SECRET_KEY = 'development key'
DEBUG = True
FACEBOOK_APP_ID = '478027312287777'
FACEBOOK_APP_SECRET = '716a15c0b0cd6490181a952fc825d5d7'
EXTENDED_PERMS = ['email', 'user_photos', 'read_mailbox', 'user_status', 'user_relationship']
app = Flask(__name__)
app.debug = DEBUG
app.secret_key = SECRET_KEY
oauth = OAuth()

facebook = oauth.remote_app('facebook',
    base_url='https://graph.facebook.com/',
    request_token_url=None,
    access_token_url='/oauth/access_token',
    authorize_url='https://www.facebook.com/dialog/oauth',
    consumer_key=FACEBOOK_APP_ID,
    consumer_secret=FACEBOOK_APP_SECRET,
    request_token_params={'scope': 'email'}
)

def checkPermissions(uid, accessToken):
    url = "https://graph.facebook.com/me?fields=permissions&access_token="+accessToken
    permissions = json.loads(urllib.urlopen(url).read())
    return permissions

def getPhotos(uid, accessToken):
    url = "https://graph.facebook.com/me?fields=photos&access_token="+accessToken
    photos = json.loads(urllib.urlopen(url).read())

    photosUploadedBy = map(lambda x:x['from'], photos['photos']['data'])  # list of dictionaries of Photo Uploader's name [{"name":<>, "id":<> }, {"name":<>, "id":<> }, {"name":<>, "id":<> }, .....]
    #print 'Photos uploaded by'
    #print photosUploadedBy
    print 'PHOTOS'
    
    # FINDING TAGGED PERSONS IN PHOTOS

    tags_list = filter(lambda y:'tags' in y.keys(), photos['photos']['data']) 
    tags_list1 = map(lambda y:y['tags'], tags_list)  
    #print 'tags list'
    #print tags_list1
    tags_data_list = map(lambda z:z['data'], tags_list1)
    #print 'tags data list'
    #print tags_data_list
    tagged_persons=list()
    for index in range(0,len(tags_data_list)):
       p=filter(lambda x:'id' in x.keys(), tags_data_list[index])
       #print 'having id'
       #print p
       #print type(p) 
       p1=map(lambda x:x['id'], p)
       tagged_persons.extend(p1)
    print 'tagged persons'
    #print tagged_persons   # list of IDs of tagged persons in all my photos (may include repetitive IDs)
    tagged_counts = Counter(tagged_persons)  # dictionary of {ID: no_of_occurences} of all tagged persons sorted in descending order of no_of_occurences
    print tagged_counts

    # FINDING LIKES FOR THE PHOTOS

    likes_list = filter(lambda y:'likes' in y.keys(), photos['photos']['data']) 
    #print likes_list
    likes_list1 = map(lambda z:z['likes'], likes_list)
    likes_data_list = map(lambda z:z['data'], likes_list1)
    #print 'likes data list'
    #print likes_data_list
    liked_by=list()
    print 'liked by'
    print type(liked_by)
    for list_elem in likes_data_list:
        p=map(lambda x:x['id'], list_elem)
        #print p
        liked_by.extend(p)
    #print liked_by   # list of IDs of persons who liked my photos (may include repetitive IDs)
    liked_counts = Counter(liked_by)  # dictionary of {ID: no_of_occurences} of all persons who liked my photos sorted in descending order of no_of_occurences
    print liked_counts 
   
    # FINDING COMMENTS FOR THE PHOTOS

    comments_list = filter(lambda y:'comments' in y.keys(), photos['photos']['data']) 
    #print comments_list
    comments_list1 = map(lambda z:z['comments'], comments_list)
    comments_data_list = map(lambda z:z['data'], comments_list1)
    #print 'comments data list'
    #print comments_data_list
    commented_by=list()
    print 'commented by'
    print type(commented_by)
    for list_elem in comments_data_list:
        p=map(lambda x:x['from']['id'], list_elem)
        #print p
        commented_by.extend(p)
    #print commented_by   # list of IDs of persons who liked my photos (may include repetitive IDs)
    commented_counts = Counter(commented_by)  # dictionary of {ID: no_of_occurences} of all tagged persons sorted in descending order of no_of_occurences
    print commented_counts
    return photos

def getCheckins(uid, accessToken):
    url = "https://graph.facebook.com/me?fields=checkins&access_token="+accessToken
    checkins = json.loads(urllib.urlopen(url).read())

    print 'CHECKINS'
    #print checkins
    #print type(checkins)
    checkins_from = map(lambda x:x['from']['id'], checkins['checkins']['data'])
    print 'checkin from'
    #print checkins_from
    checkins_from_counts = Counter(checkins_from)
    print checkins_from_counts
    checkins_tags = filter(lambda x:'tags' in x.keys(), checkins['checkins']['data'])
    checkins_tags_list = map(lambda x:x['tags']['data'], checkins_tags)
    print 'checkin tag ids' 
    #print checkins_tags_list
    checkins_tags_ids = list()
    for list_elem in checkins_tags_list:
        p=map(lambda x:x['id'], list_elem)
        #print p
        checkins_tags_ids.extend(p)
    #print checkins_tags_ids
    checkins_tags_ids_counts = Counter(checkins_tags_ids)
    print checkins_tags_ids_counts

def getFeed(uid, accessToken):
    url = "https://graph.facebook.com/me/feed?limit=50&access_token="+accessToken
    feed = json.loads(urllib.urlopen(url).read())
    #print 'data'
    #print feed['data']
    print 'FEED'
    # TAGGED NAMES

    having_story_tags = filter(lambda x:'story_tags' in x.keys(), feed['data'])
    story_tags = map(lambda x:x['story_tags'], having_story_tags)
    #print 'story tags'
    #print story_tags
    story_tag_ids=list()
    for list_index in range(0,len(story_tags)):
        for a in story_tags[list_index].values():
            story_tag_ids.extend(map(lambda x:x['id'], a))
    #print 'story_tag_ids'
    #print story_tag_ids
    story_tag_ids_counts = Counter(story_tag_ids)
    print 'story_tag_ids_counts' 
    print story_tag_ids_counts     

    # LIKED BY NAMES
    
    having_likes = filter(lambda x:'likes' in x.keys(), feed['data'])
    likes = map(lambda x:x['likes']['data'], having_likes)
    #print 'likes'
    #print likes
    likes_ids = list()
    for list_elem in likes:
        likes_ids.extend(map(lambda x:x['id'], list_elem))
    #print 'likes ids'
    #print likes_ids 
    likes_ids_counts = Counter(likes_ids)
    print 'likes ids counts'  
    print likes_ids_counts

    # COMMENTED BY NAMES

    having_comments = filter(lambda x:'comments' in x.keys(), feed['data'])
    comments = map(lambda x:x['comments']['data'], having_comments)
    #print 'comments'
    #print comments
    comments_ids = list()
    for list_elem in comments:
        comments_ids.extend(map(lambda x:x['from']['id'], list_elem))
    #print 'comments ids'
    #print comments_ids 
    comments_ids_counts = Counter(comments_ids)
    print 'comments ids counts'  
    print comments_ids_counts

def getLinks(uid, accessToken):
    url = "https://graph.facebook.com/me/links?limit=50&access_token="+accessToken
    links = json.loads(urllib.urlopen(url).read())
    #print 'data'
    #print links['data']
    print 'LINKS'
    # TAGGED NAMES

    having_story_tags = filter(lambda x:'story_tags' in x.keys(), links['data'])
    story_tags = map(lambda x:x['story_tags'], having_story_tags)
    #print 'story tags'
    #print story_tags
    story_tag_ids=list()
    for list_index in range(0,len(story_tags)):
        for a in story_tags[list_index].values():
            story_tag_ids.extend(map(lambda x:x['id'], a))
    #print 'story_tag_ids'
    #print story_tag_ids
    story_tag_ids_counts = Counter(story_tag_ids)
    print 'story_tag_ids_counts' 
    print story_tag_ids_counts     
 
    # LIKED BY NAMES
    having_likes = filter(lambda x:'likes' in x.keys(), links['data'])
    likes = map(lambda x:x['likes']['data'], having_likes)
    #print 'likes'
    #print likes
    likes_ids = list()
    for list_elem in likes:
        likes_ids.extend(map(lambda x:x['id'], list_elem))
    #print 'likes ids'
    #print likes_ids 
    likes_ids_counts = Counter(likes_ids)
    print 'likes ids counts'  
    print likes_ids_counts

    # COMMENTED BY NAMES

    having_comments = filter(lambda x:'comments' in x.keys(), links['data'])
    comments = map(lambda x:x['comments']['data'], having_comments)
    #print 'comments'
    #print comments
    comments_ids = list()
    for list_elem in comments:
        comments_ids.extend(map(lambda x:x['from']['id'], list_elem))
    #print 'comments ids'
    #print comments_ids 
    comments_ids_counts = Counter(comments_ids)
    print 'comments ids counts'  
    print comments_ids_counts

        
def getFamily(uid, accessToken):
    url = "https://graph.facebook.com/me?fields=family&access_token="+accessToken
    family = json.loads(urllib.urlopen(url).read())
    print 'FAMILY'
    #print 'data'
    #print family['family']['data']
    having_family_ids = filter(lambda x:'id' in x.keys(), family['family']['data'])
    family_ids = map(lambda x:x['id'], having_family_ids)
    print 'family ids'
    print family_ids
    
def getUID(accessToken):
    url = "https://graph.facebook.com/me?fields=id&access_token="+accessToken
    data = urllib.urlopen(url).read()
    uid=data[7:len(data)-2]
    return uid

def getProfile(uid):
    query = "SELECT username, name, about_me, birthday_date, contact_email FROM user WHERE uid = " + uid 
    query = urllib.quote(query)
    url = "https://graph.facebook.com/fql?q=" + query
    profile = json.loads(urllib.urlopen(url).read())
    print type(profile)
    return profile

def getFriends(accessToken, uid):
    #query = "SELECT name from user where uid in (SELECT uid2 FROM friend WHERE uid1 = " + uid + ")" 
    query = "SELECT uid2 FROM friend WHERE uid1 = " + uid
    params = urllib.urlencode({'q': query, 'access_token': accessToken})

    url = "https://graph.facebook.com/fql?" + params
    friends = json.loads(urllib.urlopen(url).read())
    print type(friends)
    return friends

def getName(my_id):
    query = "SELECT first_name, last_name FROM user WHERE uid = \""+my_id+"\""
    print(query) 
    query = urllib.quote(query)
    print(query) 
    url = "https://graph.facebook.com/fql?q=" + query
    data = urllib.urlopen(url).read()
    print(data)

def count_msg(x):
    if 'comments' in x.keys():
       return len(x['comments']['data'])
    else:
       return 1

def getInbox(my_id,accessToken):

   # url = "https://graph.facebook.com/me/inbox?fields=id,from,message,subject,unread,to,unseen,updated_time,comments&limit=500&access_token="+accessToken 
    
    url = "https://graph.facebook.com/me/inbox?limit=500&access_token="+accessToken 
    jsonmsg = json.loads(urllib.urlopen(url).read())
    my_inbox_data = jsonmsg['data']
    
    print 'INBOX'

    my_inbox_data = filter(lambda x: len(x['to']['data'])>=2 ,my_inbox_data)
    
    tmp = map(lambda x: len(x['to']['data']) ,my_inbox_data)
    
    toUsers = map(lambda x:x['to'],my_inbox_data)
    
    toUsers1 = map(lambda x: x['data'] ,toUsers)
    
    toUsers2 = map(lambda x: filter(lambda x1: x1['id']!=my_id ,x) ,toUsers1) 
     
    
    my_inbox_to = map(lambda x: map(lambda x1: x1['id'] ,x) ,toUsers2)
   
    
    my_inbox_comments = map(lambda x: count_msg(x) ,my_inbox_data)
    
    my_inbox_ut = map(lambda x: x['updated_time'] ,my_inbox_data)

    # lists of lists
    #my_inbox = map(lambda x,y,z: [x,y,z] ,my_inbox_to,my_inbox_comments,my_inbox_ut)  
    my_inbox = []
    tmp = map(lambda x,y,z: map(lambda x1: [x1,y,z] ,x) ,my_inbox_to,my_inbox_comments,my_inbox_ut)
    
    for x in tmp:
     my_inbox.extend(map(lambda x1: x1,x))
    
    tmp_to = list(set(map(lambda x: x[0], my_inbox)))
    #print tmp_to
    
    tmp_ib = map(lambda x: filter(lambda y: y[0] == x ,my_inbox) ,tmp_to)
    #print "****",tmp_ib
    
    def getib(li):
      id1 = map(lambda x: x[0] ,li)[0]
      cnt = sum(map(lambda x: x[1] ,li))
      time = max(map(lambda x : x[2] ,li))
      return [id1,cnt,time]
      
    my_inbox = map(lambda x: getib(x),tmp_ib)    
    
    return my_inbox


def get_status(my_id,accessToken):
   url = "https://graph.facebook.com/me/statuses?limit=500&access_token="+accessToken 
   jsonmsg = json.loads(urllib.urlopen(url).read())
   print 'STATUS' 
   status_data = jsonmsg['data']
       
   status_comm = filter(lambda x: 'comments' in x.keys(),status_data)
   status_comm_data = map(lambda x: x['comments']['data'] ,status_comm)
   status_tag = filter(lambda x: 'tags' in x.keys(),status_data)
   status_tag_data = map(lambda x: x['tags']['data'] ,status_tag)
   status_likes = filter(lambda x: 'likes' in x.keys(),status_data)
   status_likes_data = map(lambda x: x['likes']['data'] ,status_likes)
   
   # map
   user_comm = map(lambda x: map(lambda x1: x1['from']['id'],x) ,status_comm_data)
   user_comm1 = []
   for x in user_comm:
     user_comm1.extend(x)
   user_likes = map(lambda x: map(lambda x1: x1['id'],x) ,status_likes_data)
   user_likes1 = []
   for x in user_likes:
     user_likes1.extend(x)
   user_tags = map(lambda x: map(lambda x1: x1['id'],x) ,status_tag_data)
   user_tags1 = []
   for x in user_tags:
     user_tags1.extend(x)
 
   # filter userid
   user_comm1 = filter(lambda x: x!=my_id,user_comm1)
   user_likes1 = filter(lambda x: x!=my_id,user_likes1)
   user_tags1 = filter(lambda x: x!=my_id,user_tags1)
   
   # find counts
   user_comm1 = Counter(user_comm1)
   user_likes1 = Counter(user_likes1)
   user_tags1 = Counter(user_tags1)
   
   
   #No need 
   #user_comm_wtags = filter(lambda x: 'message_tags' in x.keys(),status_comm)
   
   print "\ncomm :",user_comm,"\n",user_comm1
   print "\nlikes :",user_likes,"\n",user_likes1
   print "\ntag :",user_tags,"\n",user_tags1

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login')
def login():
    return facebook.authorize(callback=url_for('facebook_authorized',
        next=request.args.get('next') or request.referrer or None,
        _external=True))


@app.route('/login/authorized')
@facebook.authorized_handler
def facebook_authorized(resp):
    if resp is None:
        return 'Access denied: reason=%s error=%s' % (
            request.args['error_reason'],
            request.args['error_description']
        )
    session['oauth_token'] = (resp['access_token'], '')
    me = facebook.get('/me')
    my_id = getUID(resp['access_token'])
    print my_id 
    #my_profile = getProfile(my_id)
    #print my_profile
    #my_friends = getFriends(resp['access_token'], my_id)
    #print my_friends

    permi = checkPermissions(my_id, resp['access_token'])
    print permi['permissions']['data'][0]
    #if 'read_mailbox' in permi['permissions']['data'][0]:
    #   getMessages(my_id, resp['access_token'])
    my_inbox = getInbox(my_id,resp['access_token'])
    print my_inbox
        
    photos = getPhotos(my_id, resp['access_token'])

    getCheckins(my_id, resp['access_token']) 
    
    getFeed(my_id, resp['access_token'])

    getFamily(my_id, resp['access_token'])

    my_status = get_status(my_id,resp['access_token'])

    getLinks(my_id, resp['access_token'])

    return 'Logged in as id=%s name=%s redirect=%s access token=%s data=%s' % \
        (me.data['id'], me.data['name'], request.args.get('next'), resp['access_token'], me.data)
    
@facebook.tokengetter
def get_facebook_oauth_token():
    return session.get('oauth_token')

if __name__ == '__main__':
    app.run()
