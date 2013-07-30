import urllib, json

YOUR_ACCESS_TOKEN="CAAGyw2gkUCEBAJhWxWe46FM80bj0GkqJTgDc4OVV5hclkI9tBu7G3uriCWEB1Vl0E3qYNMBrtZB3f80omDdHBb3JcuoGutZCKxdWtuVfpkZCdKlFPIwoo8kTwZCBr2bKqWnG9A7Co1jOyJZA0HkzA"

def getUID(accessToken):
	url = "https://graph.facebook.com/me?fields=id&access_token="+accessToken
	data = urllib.urlopen(url).read()
	uid=data[7:len(data)-2]
	return uid

def getProfile(uid):
	query = "SELECT username, name, about_me, birthday_date, contact_email FROM user WHERE uid = " + uid 
	query = urllib.quote(query)
	url = "https://graph.facebook.com/fql?q=" + query
	profile = urllib.urlopen(url).read()
	return profile

def getFriends(accessToken, uid):
	query = "SELECT name from user where uid in (SELECT uid2 FROM friend WHERE uid1 = " + uid + ")" 
	params = urllib.urlencode({'q': query, 'access_token': accessToken})

	url = "https://graph.facebook.com/fql?" + params
	friends = json.loads(urllib.urlopen(url).read())
	return friends


uid=getUID(YOUR_ACCESS_TOKEN)
my_profile=getProfile(uid)
print(my_profile)
my_friends=getFriends(YOUR_ACCESS_TOKEN,uid)
print(my_friends)
