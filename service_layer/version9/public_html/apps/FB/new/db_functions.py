"""
   MongoAlchemy Operations for Graphical Facebook Client
   1) Creates MongoDB Document Structures
   2) Stores User records (Insert/Update)   
"""

# INITIALIZATIONS

from mongoalchemy.document import Document, Index
from mongoalchemy.fields import *
from mongoalchemy.session import Session
import datetime

# DOCUMENTS

class Score(Document):
    friend_uid = StringField()
    score = FloatField()

class User(Document):
    uid = StringField()
    modified_time = DateTimeField()
    set_of_scores = ListField(DocumentField(Score), 
                              min_capacity=0, 
                              max_capacity=20)

# METHODS

session = Session.connect('fb-closest-friends')

def store_user_record(my_uid, my_friends_scores, update_flag):
    """
         Store Scores as <id>, <modified time>, <set of friends scores>
    """

    if update_flag == 1:
        current_user = session.query(User)
        current_user.set(User.set_of_scores, my_friends_scores).execute()
        current_user.set(User.modified_time, datetime.datetime.now()).execute()
        print 'Update Success'
    else:
        current_user = User(uid=my_uid, 
                            modified_time = datetime.datetime.now(), 
                            set_of_scores=my_friends_scores)
        try:
            session.insert(current_user)
            print 'Insert Success'
        except BadFieldException:
            print 'Already Inserted'

