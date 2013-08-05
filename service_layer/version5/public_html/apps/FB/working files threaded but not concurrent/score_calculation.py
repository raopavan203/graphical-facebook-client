import operator

score_list = {}
sorted_score_list = {}

def init_scores(friend_list): 
    print 'init_scores'
    for current_friend in friend_list:
        score_list[current_friend['id']] = 1
    #print score_list

def update_scores(obj, weight):   # obj is a dictionary of the form {<id>:<count>}
    print 'update_scores'
    for key in obj.keys():
        if key in score_list.keys():
            score_list[key] = score_list[key] * obj[key] * weight
    #sorted_score_list = sorted(score_list.iteritems(), key=operator.itemgetter(1))
    #print sorted_score_list

def update_scores_family(obj, weight): # obj is a list of [id]s
    print 'update_scores_family'
    for list_elem in obj:
        if list_elem in score_list.keys():
            score_list[list_elem] = score_list[list_elem] * weight
    #sorted_score_list = sorted(score_list.iteritems(), key=operator.itemgetter(1))
    #print sorted_score_list

def update_scores_inbox(obj, weight): # obj is a list of [[id, msg_count, timestamp]]s
    print 'update_scores_inbox'
    for list_elem in obj:
        if list_elem[0] in score_list.keys():
            score_list[list_elem[0]] = score_list[list_elem[0]] * list_elem[1] * weight
    #sorted_score_list = sorted(score_list.iteritems(), key=operator.itemgetter(1))
    #print sorted_score_list
    
def show_scores():   # prints score list in ascending order of scores
    
    sorted_score_list = sorted(score_list.iteritems(), key=operator.itemgetter(1))
    #print sorted_score_list
    return sorted_score_list
