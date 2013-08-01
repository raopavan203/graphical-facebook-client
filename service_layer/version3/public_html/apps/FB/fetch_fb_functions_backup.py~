from flask import Flask, jsonify, render_template, request, redirect, url_for, session

import urllib, json

def checkPermissions(accessToken):

    """returns permissions approved by user for app"""

    url = "https://graph.facebook.com/me?fields=permissions&access_token="+accessToken
    permissions = json.loads(urllib.urlopen(url).read())
    return permissions

def getFriends(accessToken):

    """returns user's friends"""

    url = "https://graph.facebook.com/me?fields=friends&access_token="+accessToken
    friends = json.loads(urllib.urlopen(url).read())
    return friends


def getProfile(accessToken, uid):

    """" returns given uid's profile info"""

    url = "https://graph.facebook.com/" + uid + "?fields=id, name, gender, relationship_status, picture.height(200).width(200), link &access_token="+accessToken
    data = urllib.urlopen(url).read()
    #print "PROFILE: ",data
    return data


def getPhotos(accessToken):

    """returns persons tagged in user's photos as well as persons who liked/commented on user's photos"""
    print 'in getPhotos'
    url = "https://graph.facebook.com/me?fields=photos&access_token="+accessToken
    photos = json.loads(urllib.urlopen(url).read())
    #print photos
    photosUploadedBy = map(lambda x:x['from'], photos['photos']['data'])  # list of dictionaries of Photo Uploader's name [{"name":<>, "id":<> }, {"name":<>, "id":<> }, {"name":<>, "id":<> }, .....]
    #print 'Photos uploaded by'
    #print photosUploadedBy
    #print 'PHOTOS'
    
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
    tagged_counts = dict((i,tagged_persons.count(i)) for i in tagged_persons)  # dictionary of {ID: no_of_occurences} of all tagged persons sorted in descending order of no_of_occurences
    #print tagged_counts

    # FINDING LIKES FOR THE PHOTOS

    likes_list = filter(lambda y:'likes' in y.keys(), photos['photos']['data']) 
    #print likes_list
    likes_list1 = map(lambda z:z['likes'], likes_list)
    likes_data_list = map(lambda z:z['data'], likes_list1)
    #print 'likes data list'
    #print likes_data_list
    liked_by=list()
    print 'liked by'
    #print type(liked_by)
    for list_elem in likes_data_list:
        p=map(lambda x:x['id'], list_elem)
        #print p
        liked_by.extend(p)
    #print liked_by   # list of IDs of persons who liked my photos (may include repetitive IDs)

    liked_counts = dict((i,liked_by.count(i)) for i in liked_by)  # dictionary of {ID: no_of_occurences} of all persons who liked my photos sorted in descending order of no_of_occurences
    #print liked_counts 
   
    # FINDING COMMENTS FOR THE PHOTOS

    comments_list = filter(lambda y:'comments' in y.keys(), photos['photos']['data']) 
    #print comments_list
    comments_list1 = map(lambda z:z['comments'], comments_list)
    comments_data_list = map(lambda z:z['data'], comments_list1)
    #print 'comments data list'
    #print comments_data_list
    commented_by=list()
    print 'commented by'
    #print type(commented_by)
    for list_elem in comments_data_list:
        p=map(lambda x:x['from']['id'], list_elem)
        #print p
        commented_by.extend(p)
    #print commented_by   # list of IDs of persons who liked my photos (may include repetitive IDs)

    commented_counts = dict((i,commented_by.count(i)) for i in commented_by)  # dictionary of {ID: no_of_occurences} of all tagged persons sorted in descending order of no_of_occurences
    #print commented_counts
    photo_data = {'tagged': tagged_counts, 'liked by': liked_counts, 'commented by': commented_counts}
    #print 'PHOTO DATA'
    #print photo_data
    return photo_data

def getCheckins(accessToken, uid):

    """returns persons tagged in user's checkins and persons who checked in with user"""

    url = "https://graph.facebook.com/me?fields=checkins&access_token="+accessToken
    checkins = json.loads(urllib.urlopen(url).read())
    
    print 'in getCHECKINS'
    print checkins
    #print type(checkins)
    
    # CHECKINS FROM PERSONS
    if 'checkins' in checkins.keys():
       print 'yessss'
       having_checkins = checkins['checkins']
       print having_checkins
       if 'data' in having_checkins.keys():
          having_data = having_checkins['data']
           
          print having_data
          having_from = filter(lambda x:'from' in x.keys(), having_data)
          print having_from
          checkins_from = map(lambda x:x['from']['id'], having_from)
          checkins_from = filter(lambda x: x!=uid,checkins_from)
          print 'checkin from'
          #print checkins_from
          checkins_from_counts = dict((i,checkins_from.count(i)) for i in checkins_from)
          print checkins_from_counts  
    
          # PERSONS TAGGED
   
          having_tags = filter(lambda x:'tags' in x.keys(), having_data)
          checkins_tags = map(lambda x:x['tags'], having_tags)
          
          print '//////', checkins_tags

          having_data = filter(lambda x:'data' in x.keys(), checkins_tags)
          checkins_data = map(lambda x:x['data'], having_data)

          print '*****', checkins_data

          checkins_tags_ids = list()

          for elem in checkins_data:
              checkins_tags_ids.extend(map(lambda x:x['id'], elem))

          print '&&&&&',checkins_tags_ids

          checkins_tags_ids_counts = dict((i,checkins_tags_ids.count(i)) for i in checkins_tags_ids)
          print checkins_tags_ids_counts

          print 'CHECKIN DATA'
          checkin_data = {'from': checkins_from_counts, 'tagged': checkins_tags_ids_counts}
          print checkin_data
          return checkin_data
    return None


def getFeed(accessToken):
 
    """returns persons tagged in user's feeds, persons who liked/commented on user's feeds"""

    url = "https://graph.facebook.com/me/feed?limit=50&access_token="+accessToken
    feed = json.loads(urllib.urlopen(url).read())
    #print 'data'
    #print feed['data']
    #print 'FEED'

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

    story_tag_ids_counts = dict((i,story_tag_ids.count(i)) for i in story_tag_ids)
    #print 'story_tag_ids_counts' 
    #print story_tag_ids_counts     

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
    likes_ids_counts = dict((i,likes_ids.count(i)) for i in likes_ids)
    #print 'likes ids counts'  
    #print likes_ids_counts

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
    comments_ids_counts = dict((i,comments_ids.count(i)) for i in comments_ids)
    #print 'comments ids counts'  
    #print comments_ids_counts
    #print 'FEED DATA'
    feed_data = {'tagged':story_tag_ids_counts, 'liked by': likes_ids_counts, 'commented by': comments_ids_counts}
    #print feed_data
    return feed_data

def getLinks(accessToken):

    """returns persons tagged in user's links, persons who liked/commented on user's links"""

    url = "https://graph.facebook.com/me/links?limit=50&access_token="+accessToken
    links = json.loads(urllib.urlopen(url).read())
    #print 'data'
    #print links['data']
    #print 'LINKS'
    
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
    story_tag_ids_counts = dict((i,story_tag_ids.count(i)) for i in story_tag_ids)
    #print 'story_tag_ids_counts' 
    #print story_tag_ids_counts     
 
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
    likes_ids_counts = dict((i,likes_ids.count(i)) for i in likes_ids)
    #print 'likes ids counts'  
    #print likes_ids_counts

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
    comments_ids_counts = dict((i,comments_ids.count(i)) for i in comments_ids)
    #print 'comments ids counts'  
    #print comments_ids_counts
    #print 'LINKS DATA'
    links_data = {'tagged':story_tag_ids_counts, 'liked by':likes_ids_counts, 'commented by':comments_ids_counts}
    #print links_data
    return links_data

def getFamily(accessToken):

    """returns persons in user's family"""

    url = "https://graph.facebook.com/me?fields=family&access_token="+accessToken
    family = json.loads(urllib.urlopen(url).read())
    print 'FAMILY'
    print 'data'
    if 'data' in family.keys():
       print family['family']['data']
       having_family_ids = filter(lambda x:'id' in x.keys(), family['family']['data'])
       family_ids = map(lambda x:x['id'], having_family_ids)
       #print 'family ids'
       #print family_ids
       return family_ids
    return None

def count_msg(x):

    """ returns count of msgs in user's chat with a particular person"""

    if 'comments' in x.keys():
       return len(x['comments']['data'])
    else:
       return 1

def getInbox(accessToken, uid):

    """ returns no. of msgs and last timestamp of user's chat with few persons user recently chatted with""" 
    print 'in getInbox'
  
    url = "https://graph.facebook.com/me/inbox?limit=500&access_token="+accessToken 
    jsonmsg = json.loads(urllib.urlopen(url).read())
    my_inbox_data = jsonmsg['data']
    
    #print 'INBOX'

    my_inbox_data = filter(lambda x: len(x['to']['data'])>=2 ,my_inbox_data)
    
    tmp = map(lambda x: len(x['to']['data']) ,my_inbox_data)
    
    toUsers = map(lambda x:x['to'],my_inbox_data)
    
    toUsers1 = map(lambda x: x['data'] ,toUsers)
    
    toUsers2 = map(lambda x: filter(lambda x1: x1['id']!=uid ,x) ,toUsers1) 
     
    
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

def get_status(accessToken, uid):

   """returns persons tagged in user's statuses and persons who liked/commented on them"""

   print 'in STATUS' 
   url = "https://graph.facebook.com/me/statuses?limit=50&access_token="+accessToken 
   jsonmsg = json.loads(urllib.urlopen(url).read())
   print jsonmsg
   status_data = jsonmsg['data']
   #print status_data
       
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
   user_comm1 = filter(lambda x: x!=uid,user_comm1)
   user_likes1 = filter(lambda x: x!=uid,user_likes1)
   user_tags1 = filter(lambda x: x!=uid,user_tags1)
   
   # find counts
   user_comm1 = dict((i,user_comm1.count(i)) for i in user_comm1)
   user_likes1 = dict((i,user_likes1.count(i)) for i in user_likes1)
   user_tags1 = dict((i,user_tags1.count(i)) for i in user_tags1)
   
   
   #No need 
   #user_comm_wtags = filter(lambda x: 'message_tags' in x.keys(),status_comm)
   
   #print "\ncomm :",user_comm,"\n",user_comm1
   #print "\nlikes :",user_likes,"\n",user_likes1
   #print "\ntag :",user_tags,"\n",user_tags1

   #print 'STATUS DATA'
   status_data = {'tagged':user_tags1, 'liked by':user_likes1, 'commented by':user_comm1}
   #print status_data
   return status_data

