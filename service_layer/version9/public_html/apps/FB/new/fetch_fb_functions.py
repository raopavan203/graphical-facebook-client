import urllib, json
base_url = "https://graph.facebook.com/"

class FacebookDataHandler():
    accessToken = ""
    def __init__(self, accessToken):
        self.accessToken = accessToken

    def set_accessToken(self, accessToken):
        self.accessToken = accessToken

    def checkPermissions(self):
        """returns permissions approved by user for app"""

        url = base_url + "me?fields=permissions&access_token=" + self.accessToken
        try:
           permissions = json.loads(urllib.urlopen(url).read())
        except URLError:
           try:
              permissions = json.loads(urllib.urlopen(url).read())
           except URLError:
              return None
           
        if 'permissions' in permissions.keys():
           return permissions['permissions']
        return None

    def getFriends(self):
        """returns user's friends"""

        url = base_url + "me?fields=friends&access_token=" + self.accessToken
        try:
           friends = json.loads(urllib.urlopen(url).read()) 
        except URLError:
           try:
              friends = json.loads(urllib.urlopen(url).read()) 
           except URLError:
              return None       
        return friends

    def getProfile(self, uid):
        """" returns given uid's profile info"""

        url = base_url + uid + "?fields=id, name, gender, relationship_status, \
picture.height(200).width(200), link, statuses.limit(1).fields(message,updated_time) \
&access_token=" + self.accessToken
        try:
           data = urllib.urlopen(url).read()
        except URLError:
           try:
              data = urllib.urlopen(url).read()
           except URLError:
              return None       
        return data

    def getData(self, uid, fetch_string):
        """ fetches the fields mentioned in fetch_string for uid from FB GRAPH API"""    
        url = base_url + uid + "?fields=" + fetch_string + "&access_token=" + self.accessToken
        try:
           all_data = json.loads(urllib.urlopen(url).read())
        except URLError:
           try:
              all_data = json.loads(urllib.urlopen(url).read())
           except URLError:
              return None       
        return all_data

    def getFriendLists(self, all_data):
        """returns persons in user's friend lists of type 1=close_friends 2=work \ 
           3=education 4=user_created 5=current_city"""

        print 'FRIEND LIST'
        if 'friendlists' in all_data.keys():
         if 'data' in all_data['friendlists'].keys():
           friendlist_data={}
           friendlist_data['close_friends']=[]
           friendlist_data['work']=[]
           friendlist_data['education']=[]  
           friendlist_data['user_created']=[]
           friendlist_data['current_city']=[]
           for list_elem in all_data['friendlists']['data']:
               if 'list_type' in list_elem.keys() and 'members' in list_elem.keys():
                   having_id = filter(lambda x:'id' in x.keys(), list_elem['members']['data'])         
                   id_list = map(lambda x:x['id'], having_id)                                         
                   if list_elem['list_type']=='close_friends':
                      friendlist_data['close_friends'].extend(id_list)       
                   if list_elem['list_type']=='work':
                      friendlist_data['work'].extend(id_list)       
                   if list_elem['list_type']=='education':
                      friendlist_data['education'].extend(id_list)       
                   if list_elem['list_type']=='user_created':
                      friendlist_data['user_created'].extend(id_list)       
                   if list_elem['list_type']=='current_city':
                      friendlist_data['current_city'].extend(id_list)       
           return friendlist_data
        return None  

    def splitPhotos(self, all_data, uid, pics_by_me, pics_by_others):
        print 'SPLIT PHOTOS'
        if 'photos' in all_data.keys():
           photos = all_data['photos']
           dict_list = photos['data']
           for d in dict_list:
              if d['from']['id'] == uid:
                 pics_by_me.append(d)         
              else:
                 pics_by_others.append(d)
           return 'Photos Available'
        return None

    def splitPhotosByTagCount(self, pics, few_tags_pics, many_tags_pics):
        tags_list = filter(lambda y:'tags' in y.keys(), pics) 
        for list_elem in tags_list:
           if len(list_elem['tags']['data']) > 5:
              many_tags_pics.append(list_elem)
           else:
              few_tags_pics.append(list_elem)

    def getPhotos(self, pics, pics_with_tags, uid):
        """returns persons tagged in user's photos as well as persons \
           who liked/commented on user's photos"""

        print 'GET PHOTOS'
 
        # FINDING TAGGED PERSONS IN PHOTOS
        
        tags_list1 = map(lambda y:y['tags'], pics_with_tags)  
        tags_data_list = map(lambda z:z['data'], tags_list1)
        tagged_persons=list()
        for index in range(0,len(tags_data_list)):
          having_id=filter(lambda x:'id' in x.keys(), tags_data_list[index])
          idd=map(lambda x:x['id'], having_id)
          no_nones = filter(lambda x:x!=None, idd) 
          tagged_persons.extend(no_nones)
        tagged_counts = dict((i,tagged_persons.count(i)) for i in tagged_persons)  
        # dictionary of {ID: no_of_occurences} of all tagged persons sorted 
        # in descending order of no_of_occurences

        # FINDING LIKES FOR THE PHOTOS

        likes_list = filter(lambda y:'likes' in y.keys(), pics) 
        likes_list1 = map(lambda z:z['likes'], likes_list)
        likes_data_list = map(lambda z:z['data'], likes_list1)
        liked_by=list()
        for list_elem in likes_data_list:
           having_id=filter(lambda x:'id' in x.keys(), list_elem)
           idd=map(lambda x:x['id'], having_id)
           no_nones = filter(lambda x:x!=None, idd)
           liked_by.extend(no_nones)
 
        liked_counts = dict((i,liked_by.count(i)) for i in liked_by)  
        # dictionary of {ID: no_of_occurences} of all persons who liked 
        # my photos sorted in descending order of no_of_occurences
   
        # FINDING COMMENTS FOR THE PHOTOS

        comments_list = filter(lambda y:'comments' in y.keys(), pics) 
        comments_list1 = map(lambda z:z['comments'], comments_list)
        comments_data_list = map(lambda z:z['data'], comments_list1)
        commented_by=list()
        for list_elem in comments_data_list:
           having_from = filter(lambda x:'from' in x.keys(), list_elem)
           fromm = map(lambda x:x['from'], list_elem)
           no_nones = filter(lambda x:x!=None, fromm)
           having_id = filter(lambda x:'id' in x.keys(), no_nones) 
           idd = map(lambda x:x['id'], having_id)
           commented_by.extend(idd)

        commented_counts = dict((i,commented_by.count(i)) for i in commented_by)  
        # dictionary of {ID: no_of_occurences} of all tagged persons 
        # sorted in descending order of no_of_occurences
        photo_data = {'tagged': tagged_counts, 
                      'liked by': liked_counts, 
                      'commented by': commented_counts}
        return photo_data

    def getCheckins(self, uid, all_data):
        """returns persons tagged in user's checkins and persons who checked in with user"""

        print 'GET CHECKINS'
        if 'checkins' in all_data.keys():
         checkins = all_data['checkins']

         # CHECKINS FROM PERSONS

         if 'data' in checkins.keys():
          having_data = checkins['data']
          having_from = filter(lambda x:'from' in x.keys(), having_data)
          fromm = map(lambda x:x['from'], having_from)
          no_nones = filter(lambda x:x!=None, fromm)
          having_id = filter(lambda x:'id' in x.keys(), no_nones) 
          checkins_from = map(lambda x:x['id'], having_id)
          checkins_from = filter(lambda x: x!=uid,checkins_from)
          checkins_from_counts = dict((i,checkins_from.count(i)) for i in checkins_from)
    
          # PERSONS TAGGED
   
          having_tags = filter(lambda x:'tags' in x.keys(), having_data)
          checkins_tags = map(lambda x:x['tags'], having_tags)         

          having_data = filter(lambda x:'data' in x.keys(), checkins_tags)
          checkins_data = map(lambda x:x['data'], having_data)

          checkins_tags_ids = list()

          for elem in checkins_data:
              checkins_tags_ids.extend(map(lambda x:x['id'], elem))

          checkins_tags_ids_counts = dict((i,checkins_tags_ids.count(i)) for i in checkins_tags_ids)
          checkin_data = {'from': checkins_from_counts, 
                          'tagged': checkins_tags_ids_counts}
          return checkin_data
        return None

    def splitFeed(self, all_data, uid, feed_by_me, feed_by_others):
        print 'SPLIT FEED'

        if 'feed' in all_data.keys():
           feed = all_data['feed']
           dict_list = feed['data']
           for d in dict_list:
             if d['from']['id'] == uid:
               feed_by_me.append(d)         
             else:
               feed_by_others.append(d)
           return 'Feed Available'
        return None

    def getFeed(self, feed):
        """returns persons tagged in user's feeds, \
           persons who liked/commented on user's feeds"""   

        print 'FEED'
     
        # TAGGED NAMES
        
        having_story_tags = filter(lambda x:'story_tags' in x.keys(), feed)
        story_tags = map(lambda x:x['story_tags'], having_story_tags)
        story_tag_ids=list()
        for list_index in range(0,len(story_tags)):
            for a in story_tags[list_index].values():
                having_id = filter(lambda x:'id' in x.keys(), a)
                idd = map(lambda x:x['id'], having_id)
                no_nones = filter(lambda x:x!=None, idd)               
                story_tag_ids.extend(no_nones)

        story_tag_ids_counts = dict((i,story_tag_ids.count(i)) for i in story_tag_ids)

        # LIKED BY NAMES
        
        having_likes = filter(lambda x:'likes' in x.keys(), feed)
        likes = map(lambda x:x['likes']['data'], having_likes)
        likes_ids = list()
        for list_elem in likes:
            having_id = filter(lambda x:'id' in x.keys(), list_elem) 
            idd = map(lambda x:x['id'], having_id)
            no_nones = filter(lambda x:x!=None, idd)
            likes_ids.extend(no_nones)
        likes_ids_counts = dict((i,likes_ids.count(i)) for i in likes_ids)

        # COMMENTED BY NAMES

        having_comments = filter(lambda x:'comments' in x.keys(), feed)
        comments = map(lambda x:x['comments']['data'], having_comments)
        comments_ids = list()
        for list_elem in comments:
            having_from = filter(lambda x:'from' in x.keys(), list_elem)
            fromm = map(lambda x:x['from'], list_elem)
            no_nones = filter(lambda x:x!=None, fromm)
            having_id = filter(lambda x:'id' in x.keys(), no_nones) 
            idd = map(lambda x:x['id'], having_id)
            comments_ids.extend(idd)
        comments_ids_counts = dict((i,comments_ids.count(i)) for i in comments_ids)
        feed_data = {'tagged':story_tag_ids_counts, 
                     'liked by': likes_ids_counts, 
                     'commented by': comments_ids_counts}
        return feed_data

    def getLinks(self, all_data):
        """returns persons tagged in user's links, persons who liked/commented on user's links"""
      
        print 'LINKS'

        if 'links' in all_data.keys():
           links = all_data['links']

           having_story_tags = filter(lambda x:'story_tags' in x.keys(), links['data'])
           story_tags = map(lambda x:x['story_tags'], having_story_tags)
           story_tag_ids=list()
           for list_index in range(0,len(story_tags)):
               for a in story_tags[list_index].values():
                  having_id = filter(lambda x:'id' in x.keys(), a)
                  idd = map(lambda x:x['id'], having_id)
                  no_nones = filter(lambda x:x!=None, idd)
                  story_tag_ids.extend(no_nones)
           story_tag_ids_counts = dict((i,story_tag_ids.count(i)) for i in story_tag_ids)
     
           # LIKED BY NAMES
           having_likes = filter(lambda x:'likes' in x.keys(), links['data'])
           likes = map(lambda x:x['likes']['data'], having_likes)
           likes_ids = list()
           for list_elem in likes:
              having_id = filter(lambda x:'id' in x.keys(), list_elem)
              idd = map(lambda x:x['id'], having_id)
              no_nones = filter(lambda x:x!=None, idd)
              likes_ids.extend(no_nones)
           likes_ids_counts = dict((i,likes_ids.count(i)) for i in likes_ids)

           # COMMENTED BY NAMES

           having_comments = filter(lambda x:'comments' in x.keys(), links['data'])
           comments = map(lambda x:x['comments']['data'], having_comments)
           comments_ids = list()
           for list_elem in comments:
              having_from = filter(lambda x:'from' in x.keys(), list_elem)
              fromm = map(lambda x:x['from'], list_elem)
              no_nones = filter(lambda x:x!=None, fromm)
              having_id = filter(lambda x:'id' in x.keys(), no_nones) 
              idd = map(lambda x:x['id'], having_id)
              comments_ids.extend(idd)
           comments_ids_counts = dict((i,comments_ids.count(i)) for i in comments_ids)
        
           links_data = {'tagged':story_tag_ids_counts, 
                         'liked by':likes_ids_counts, 
                         'commented by':comments_ids_counts}      
           return links_data
        return None

    def getFamily(self, all_data):
        """returns persons in user's family"""
        print 'FAMILY'
        if 'family' in all_data.keys():
           family = all_data['family']
           if 'data' in family.keys():
             having_family_ids = filter(lambda x:'id' in x.keys(), family['data'])
             family_ids = map(lambda x:x['id'], having_family_ids)
             family_ids = filter(lambda x:x!=None, family_ids)
             return family_ids
        return None

    def count_msg(self, x):
        """ returns count of msgs in user's chat with a particular person"""

        if 'comments' in x.keys():
           return len(x['comments']['data'])
        else:
           return 1

    def getInbox(self, uid, all_data):
        """ returns no. of msgs and last timestamp of user's chat with few persons user recently chatted with""" 
        
        print 'GET INBOX'
        if 'inbox' in all_data.keys():
          inbox = all_data['inbox'] 
          if 'data' in inbox.keys():
           my_inbox_data = inbox['data']
        
           my_inbox_data = filter(lambda x: len(x['to']['data'])>=2 ,my_inbox_data)
         
           tmp = map(lambda x: len(x['to']['data']) ,my_inbox_data)
        
           toUsers = map(lambda x:x['to'],my_inbox_data)
        
           toUsers1 = map(lambda x: x['data'] ,toUsers)
        
           toUsers2 = map(lambda x: filter(lambda x1: x1['id']!=uid ,x) ,toUsers1) 
              
           my_inbox_to = map(lambda x: map(lambda x1: x1['id'] ,x) ,toUsers2)
       
           my_inbox_comments = map(lambda x: self.count_msg(x) ,my_inbox_data)
        
           my_inbox_ut = map(lambda x: x['updated_time'] ,my_inbox_data)

           my_inbox = []
           tmp = map(lambda x,y,z: map(lambda x1:[x1,y,z], x), my_inbox_to, my_inbox_comments, my_inbox_ut)
        
           for x in tmp:
             my_inbox.extend(map(lambda x1: x1,x))
        
           tmp_to = list(set(map(lambda x: x[0], my_inbox)))
        
           tmp_ib = map(lambda x: filter(lambda y: y[0] == x ,my_inbox) ,tmp_to)
        
           def getib(li):
             id1 = map(lambda x: x[0] ,li)[0]
             cnt = sum(map(lambda x: x[1] ,li))
             time = max(map(lambda x : x[2] ,li))
             return [id1,cnt,time]
          
           my_inbox = map(lambda x: getib(x),tmp_ib)    
        
           return my_inbox
        return None

    def get_status(self, uid, all_data):
        """returns persons tagged in user's statuses and persons who liked/commented on them"""

        print 'GET STATUS' 

        if 'statuses' in all_data.keys():
           statuses = all_data['statuses']
           status_data = statuses['data']
           
           status_comm = filter(lambda x: 'comments' in x.keys(),status_data)
           status_comm_data = map(lambda x: x['comments']['data'] ,status_comm)
           status_tag = filter(lambda x: 'tags' in x.keys(),status_data)
           status_tag_data = map(lambda x: x['tags']['data'] ,status_tag)
           status_likes = filter(lambda x: 'likes' in x.keys(),status_data)
           status_likes_data = map(lambda x: x['likes']['data'] ,status_likes)

           # map
           user_comm = list() 
           for list_elem in status_comm_data:
              having_from = filter(lambda x:'from' in x.keys(), list_elem)
              fromm = map(lambda x:x['from'], having_from)
              no_nones = filter(lambda x:x!=None, fromm)
              having_id = filter(lambda x:'id' in x.keys(), no_nones)
              idd = map(lambda x:x['id'], having_id)
              user_comm.extend(idd) 
       
           user_likes = list()
           for list_elem in status_likes_data:
              having_id = filter(lambda x:'id' in x.keys(), list_elem)
              idd = map(lambda x:x['id'], having_id)
              no_nones = filter(lambda x:x!=None, idd)
              user_likes.extend(no_nones)

           user_tags = list()
           for list_elem in status_tag_data:
              having_id = filter(lambda x:'id' in x.keys(), list_elem)
              idd = map(lambda x:x['id'], having_id)
              no_nones = filter(lambda x:x!=None, idd)
              user_tags.extend(idd)
   
           # filter userid
           user_comm = filter(lambda x: x!=uid,user_comm)
           user_likes = filter(lambda x: x!=uid,user_likes)
           user_tags = filter(lambda x: x!=uid,user_tags)

           # find counts
           user_comm1 = dict((i,user_comm.count(i)) for i in user_comm)
           user_likes1 = dict((i,user_likes.count(i)) for i in user_likes)
           user_tags1 = dict((i,user_tags.count(i)) for i in user_tags)

           status_data = {'tagged':user_tags1, 
                          'liked by':user_likes1, 
                          'commented by':user_comm1}
           return status_data
        return None

