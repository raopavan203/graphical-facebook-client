import operator

def update_scores(obj, weight, score_list):   # obj is a dictionary of the form {<id>:<count>}
    print 'update_scores'
    for key in obj.keys():
        if key in score_list.keys():
            score_list[key] = score_list[key] * obj[key] * weight
    #sorted_score_list = sorted(score_list.iteritems(), key=operator.itemgetter(1))
    #print sorted_score_list

def update_scores_family(obj, weight, score_list): # obj is a list of [id]s
    print 'update_scores_family'
    for list_elem in obj:
        if list_elem in score_list.keys():
            score_list[list_elem] = score_list[list_elem] * weight
    #sorted_score_list = sorted(score_list.iteritems(), key=operator.itemgetter(1))
    #print sorted_score_list

def update_scores_inbox(obj, weight, score_list): # obj is a list of [[id, msg_count, timestamp]]s
    print 'update_scores_inbox'
    for list_elem in obj:
        if list_elem[0] in score_list.keys():
            score_list[list_elem[0]] = score_list[list_elem[0]] * list_elem[1] * weight
    #sorted_score_list = sorted(score_list.iteritems(), key=operator.itemgetter(1))
    #print sorted_score_list
    
def update_scores_friendlist(obj, weight, score_list): # obj is a list of [ids]
    print 'update_score_friendlists'
    for list_elem in obj:
        if list_elem in score_list.keys(): 
            score_list[list_elem] = score_list[list_elem] * weight

def show_scores(score_list):   # prints score list in ascending order of scores
    
    sorted_score_list = sorted(score_list.iteritems(), key=operator.itemgetter(1))
    #print sorted_score_list
    return sorted_score_list
