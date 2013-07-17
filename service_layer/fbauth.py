from flask import Flask, redirect, url_for, session, request
from flask_oauth import OAuth

import urllib, json

SECRET_KEY = 'development key'
DEBUG = True
FACEBOOK_APP_ID = '478027312287777'
FACEBOOK_APP_SECRET = '716a15c0b0cd6490181a952fc825d5d7'
MY_ID=""

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
    query = "SELECT name from user where uid in (SELECT uid2 FROM friend WHERE uid1 = " + uid + ")" 
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
    getName(me.data['id'])
    my_id = getUID(resp['access_token'])
    print my_id 
    my_profile = getProfile(my_id)
    print my_profile
    my_friends = getFriends(resp['access_token'], my_id)
    print my_friends
    return 'Logged in as id=%s name=%s redirect=%s access token=%s data=%s' % \
        (me.data['id'], me.data['name'], request.args.get('next'), resp['access_token'], me.data)


@facebook.tokengetter
def get_facebook_oauth_token():
    return session.get('oauth_token')

if __name__ == '__main__':
    app.run()
