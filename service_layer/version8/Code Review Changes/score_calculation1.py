import operator

class Scores():
    score_list = {}

    def __init__(self, friend_list):
       print 'init_scores'
       for current_friend in friend_list:
          self.score_list[current_friend['id']] = 1

    def update_scores(self, obj, weight):   # obj is a dictionary of the form {<id>:<count>}
       print 'update_scores'
       for key in obj.keys():
          if key in self.score_list.keys():
             self.score_list[key] = self.score_list[key] * obj[key] * weight

    def update_scores_family(self, obj, weight): # obj is a list of [id]s
       print 'update_scores_family'
       for list_elem in obj:
          if list_elem in self.score_list.keys():
             self.score_list[list_elem] = self.score_list[list_elem] * weight

    def update_scores_inbox(self, obj, weight): # obj is a list of [[id, msg_count, timestamp]]s
       print 'update_scores_inbox'
       for list_elem in obj:
          if list_elem[0] in self.score_list.keys():
             self.score_list[list_elem[0]] = self.score_list[list_elem[0]] * list_elem[1] * weight
    
    def update_scores_friendlist(self, obj, weight): # obj is a list of [ids]
       print 'update_score_friendlists'
       for list_elem in obj:
          if list_elem in self.score_list.keys(): 
             self.score_list[list_elem] = self.score_list[list_elem] * weight

    def show_scores(self):   # prints score list in ascending order of scores
       sorted_score_list = sorted(self.score_list.iteritems(), key=operator.itemgetter(1))
       return sorted_score_list
