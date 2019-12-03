from django.shortcuts import render,redirect
from django.http import HttpResponse, HttpRequest
from credentials import client_id,client_secret,headers,apiKey,gcp_access_token
from django.views.generic import TemplateView
#import pyrebase
import spotipy
import sys
import spotipy.util as util
import requests
import json

# Create your views here.
class SignInFireBaseView(TemplateView):
    def get(self,request,*args,**kwargs):
        email = request.GET.get('email')
        password = request.GET.get('psw')
        sign_in_endpoint = 'https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key='+apiKey
        sign_in_req = {
            "email":email,
            "password":password,
            "returnSecureToken":True
        }
        r = requests.post(sign_in_endpoint,data=sign_in_req)
        if r.status_code == 200:
            stringified = r.content.decode('utf8').replace("'", '"')
            idToken = json.loads(stringified)["idToken"]
            get_user_data_endpoint = 'https://identitytoolkit.googleapis.com/v1/accounts:lookup?key='+apiKey
            get_user_data_req = {
                "idToken":idToken
            }
            req = requests.post(get_user_data_endpoint,data=get_user_data_req)
            data = json.loads(req.content.decode('utf8').replace("'", '"'))
            userId = data['users'][0]['localId']
            all_users_endpoint = 'https://spotifysocialnetwork.firebaseio.com/users.json?access_token='+gcp_access_token
            all_users_req = requests.get(all_users_endpoint)
            all_users = json.loads(all_users_req.content.decode('utf8').replace("'",'"'))
            for user in all_users:
                values = all_users[user]
                if values["userId"] == userId:
                    return redirect('dashboard',_id=user)
        return render(request,"signin.html",context={})
class RegisterView(TemplateView):
    #Create user with email and password, when form is submitted, create user on firebase, and redirect to login view
    def get(self,request,*args,**kwargs):
        username = request.GET.get('uname')
        email = request.GET.get('email')
        password = request.GET.get('password')
        endpoint = 'https://identitytoolkit.googleapis.com/v1/accounts:signUp?key='+apiKey
        data = {
            "email":email,
            "password":password,
            "returnSecureToken":True
        }
        r = requests.post(endpoint,data=data)
        if r.status_code == 200:
            stringified = r.content.decode('utf8').replace("'", '"')
            toJson = json.loads(stringified)
            userId = toJson['localId']
            print('userId: ',userId)
            print('Successfully Registered user with email:{}'.format(email))
            return redirect('login',_id=userId,username=username)

        return render(request,"registration.html",context={})
class LoginView(TemplateView):
    def get(self,request,_id,username,*args,**kwargs):
        #print(_id,username)
        playlist_scopes = 'playlist-read-private,playlist-modify-public,playlist-read-collaborative,'
        spotify_connect_scopes = 'user-modify-playback-state,user-read-currently-playing,user-read-playback-state,'
        users_scopes = 'user-read-private,user-read-email,'
        library_scopes = 'user-library-modify,user-read-email,'
        listening_history_scopes = 'user-read-recently-played,user-top-read,'
        playback_scopes = 'streaming'

        scope = playlist_scopes+spotify_connect_scopes+users_scopes+library_scopes+listening_history_scopes+playback_scopes
        #username = request.GET.get('uname')
        state = 'username|' + username + '|id|' + _id
        url = 'https://accounts.spotify.com/authorize?response_type=code&client_id='+client_id+'&scope='+scope+'&redirect_uri=http://localhost:8000/authorize&state='+state
        #return render(request,'login.html',context={})
        return redirect(url)
        #token = util.prompt_for_user_token('tester', scope,client_id=client_id,client_secret=client_secret,redirect_uri='http://localhost:8000/authorize')

class AuthorizeView(TemplateView):
    def get(self,request,*args,**kwargs):
        #This view creates profiles on firebase for each user
        code = request.GET.get('code','')
        state = request.GET.get('state','').split('|')
        username = state[1]
        userId = state[3]
        auth_body = {
            'grant_type':'authorization_code',
            'code':code,
            'redirect_uri':'http://localhost:8000/authorize'
        }
        auth_request = requests.post('https://accounts.spotify.com/api/token',data=auth_body,headers=headers)
        #get data from this request's content and post that to firebase db
        json_response = auth_request.content.decode('utf8').replace("'", '"')
        #print(json_response)
        #print('- ' * 20)

        # Load the JSON to a Python list & dump it back out as formatted JSON
        data = json.loads(json_response)
        access_token = data['access_token']
        refresh_token = data['refresh_token']
        #spotify_id = data['id']
        profile_req = {
            "username":username,
            "userId":userId,
            "spotify_access":access_token,
            "spotify_refresh":refresh_token,
            "followers":[]
        }
        #Create User Profile on Firebase
        firebase_endpoint = 'https://spotifysocialnetwork.firebaseio.com/users.json?access_token='+gcp_access_token
        create_profile = requests.post(firebase_endpoint,data=json.dumps(profile_req))
        return render(request,'authorize.html',context={})

class DashboardView(TemplateView):
    def get(self,request,_id,*args,**kwargs):
        spotify_access_endpoint = 'https://spotifysocialnetwork.firebaseio.com/users/'+_id+'.json?access_token='+gcp_access_token
        r = requests.get(spotify_access_endpoint)
        if r.status_code == 200:
            stringified = r.content.decode('utf8').replace("'", '"')
            thisUser = json.loads(stringified)
        if thisUser:
            try:
                followers = {}
                for follower in thisUser['Followers']:
                    #Get user name, and id
                    followerInfoEndpoint = 'https://spotifysocialnetwork.firebaseio.com/users/'+follower+'.json?access_token='+gcp_access_token
                    r = requests.get(followerInfoEndpoint)
                    stringified = r.content.decode('utf8').replace("'", '"')
                    thisFollower = json.loads(stringified)
                    followers[follower] = thisFollower['username']
                
            except:
                followers = {}
            try:
                #print('We here')
                sp = spotipy.Spotify(auth=thisUser['spotify_access'])
                if sp:
                    playlists = sp.current_user_playlists()
                    devices = sp.devices()
                    recently_played = sp.current_user_recently_played()['items']
                    #print(recently_played[0]['track'].items())
                    recent_tracks = []
                    for track in recently_played:
                        this_track = track['track']
                        #print('THIS TRACK\n',this_track)
                        name = this_track['name']
                        artist = this_track['artists'][0]['name']
                        link = this_track['external_urls']['spotify']
                        image = this_track['album']['images'][0]['url']
                        data = {
                            "name":name,
                            "artist":artist,
                            "link":link,
                            "image":image
                        }
                        recent_tracks.append(data)
                    # print('Playlists\n',playlists,devices)
                    for playlist in playlists['items']:
                        playlist['images'] = [playlist['images'][0]]
            except:
                #Access token expired, refresh and get new
                #print('TESTING 2')
                print('Now we here boohoo')
                token_endpoint = 'https://accounts.spotify.com/api/token'
                token_req_body = {
                    "grant_type": "refresh_token",
                    "refresh_token":thisUser['spotify_refresh']
                }
                #print('MAKING REQUEST\n')
                token_req = requests.post(token_endpoint,data=token_req_body,headers=headers)
                
                #print('RESPONE\n',token_req.content)
                token_response = json.loads(token_req.content.decode('utf8').replace("'", '"'))
                new_access_token = token_response["access_token"]
                #print('NEW ACCESS\n',new_access_token)
                sp = spotipy.Spotify(auth=new_access_token)
                #print('TESTING NEW\n',sp)
                playlists = sp.current_user_playlists()
                
                #print('CALLING METHODS WITH NEW\n',playlists,'\n')
                devices = sp.devices()
                recently_played = sp.current_user_recently_played()
                #print(recently_played[0]['track'].items())
                #print(devices,'\n')
                #print(recently_played,'\n')
                recent_tracks = []
                #print(recently_played['items'])
                for track in recently_played['items']:
                    this_track = track['track']
                    #print('THIS TRACK\n',this_track)
                    name = this_track['name']
                    artist = this_track['artists'][0]['name']
                    link = this_track['external_urls']['spotify']
                    image = this_track['album']['images'][0]['url']
                    data = {
                        "name":name,
                        "artist":artist,
                        "link":link,
                        "image":image
                    }
                    recent_tracks.append(data)
                print('YO')
                for playlist in playlists['items']:
                    playlist['images'] = [playlist['images'][0]]
                #print(playlists)
                #recent = sp.current_user_recently_played()

        #print(r.content)
        try:
            return render(request,'dashboard.html',context={"uid":_id,"user":thisUser['username'],"playlists":playlists['items'],"devices":devices,"recently_played":recent_tracks,"followers":followers})
        except Exception as e:
            print(e)
            return HttpResponse('Something went wrong')

def getUser(followee):
    get_users_endpoint = 'https://spotifysocialnetwork.firebaseio.com/users.json?access_token='+gcp_access_token
    r = requests.get(get_users_endpoint)
    stringified = r.content.decode('utf8').replace("'", '"')
    users = json.loads(stringified)
    for user in users:
        spotify_access_endpoint = 'https://spotifysocialnetwork.firebaseio.com/users/'+user+'.json?access_token='+gcp_access_token
        r = requests.get(spotify_access_endpoint)
        stringified = r.content.decode('utf8').replace("'", '"')
        thisUser = json.loads(stringified)
        if thisUser['userId'] == followee:
            return user
def getPosts(followee):
    result = []
    user = getUser(followee)
    get_posts_endpoint = 'https://spotifysocialnetwork.firebaseio.com/posts.json?access_token='+gcp_access_token
    r = requests.get(get_posts_endpoint)
    print('R.content',r.content)
    stringified = r.content.decode('utf8').replace("'", '"')
    print('stringified',stringified)
    posts = json.loads(stringified)
    print('posts',posts)
    for post in posts:
        post_detail_endpoint = 'https://spotifysocialnetwork.firebaseio.com/posts/'+post+'.json?access_token='+gcp_access_token
        r = requests.get(post_detail_endpoint)
        stringified = r.content.decode('utf8').replace("'", '"')
        thisPost = json.loads(stringified)
        if 'posterId' in thisPost:
            #print(thisPost['posterId'],user)
            if thisPost['posterId'] == user:
                #print('BEEEE')
                result.append([thisPost,post])
    return result
class FeedView(TemplateView):
    def get(self,request,_id,*args,**kwargs):
        spotify_access_endpoint = 'https://spotifysocialnetwork.firebaseio.com/users/'+_id+'.json?access_token='+gcp_access_token
        r = requests.get(spotify_access_endpoint)
        noFollows = False
        if r.status_code == 200:
            stringified = r.content.decode('utf8').replace("'", '"')
            thisUser = json.loads(stringified)
        try:
            posts = []
            ids = []
            following = thisUser['Following']
            for followee in following:
                #print(getPosts(followee)[0][1])
                posts.extend(getPosts(followee))
            print(posts)

            #get user ids of all users that this user is following(profile ids)
            #get posts created by the users in this users following field
            #pass posts to context, determine how many, and sorting
        except Exception as e:
            print('hehe',e)
            following = []
        #print(thisUser)
        if not following:
            return render(request,'feed.html',context={"uid":_id,"user":thisUser['username'],"noFollows":True})

        return render(request,'feed.html',context={"uid":_id,"user":thisUser['username'],"noFollows":False,"following":following,'posts':posts})

class UsersView(TemplateView):
    def __init__(self):
        self.user_id = ''
    def getId(Followed):
        return 'ye'
    def get(self,request,_id,*args,**kwargs):
        spotify_access_endpoint = 'https://spotifysocialnetwork.firebaseio.com/users/.json?access_token='+gcp_access_token
        r = requests.get(spotify_access_endpoint)
        if r.status_code == 200:
            stringified = r.content.decode('utf8').replace("'", '"')
            allUsers = json.loads(stringified)
        canFollow = []
        self.user_id += _id
        try:
            for user in allUsers:
                if user != _id:
                    canFollow.append(allUsers[user])
        except:
            pass
        return render(request,'users.html',context={'id':_id,'canFollow':canFollow,'canFollowLength':len(canFollow)})
    def post(self,request,*args,**kwargs):
        print(request.POST.get('moiz'))
        print('BREH',self.user_id)
        return render(request,'users.html',context={})

def usersView(request,_id):
    #canFollow = []
    def getId(Followed):
        allUsersEndpoint = 'https://spotifysocialnetwork.firebaseio.com/users/.json?access_token='+gcp_access_token
        r = requests.get(allUsersEndpoint)
        stringified = r.content.decode('utf8').replace("'", '"')
        allUsers = json.loads(stringified)
        for key in allUsers:
            userId = allUsers[key]['userId']
            if userId == Followed:
                return key
        #    if allUsers[key][userId] == Followed:
        #        return key
        return 'Not found'
    def addFollower(receiver,sender):
        this_user_follower_endpoint = 'https://spotifysocialnetwork.firebaseio.com/users/'+receiver+'/Followers.json?access_token='+gcp_access_token
        get_followers_req = requests.get(this_user_follower_endpoint)
        stringified = get_followers_req.content.decode('utf8').replace("'",'"')
        existingFollowers = json.loads(stringified)
        if isinstance(existingFollowers,list):
            existingFollowers += [sender]
        else:
            existingFollowers = [sender]
        followers_body = {
            'Followers':existingFollowers
        }
        addFollowerEndpoint = 'https://spotifysocialnetwork.firebaseio.com/users/'+receiver+'.json?access_token='+gcp_access_token
        addFollowerReq = requests.patch(addFollowerEndpoint,data=json.dumps(followers_body))
        return addFollowerReq.content
    if request.method == 'GET':
        #_id = request.GET.get()
        #print('hey')
        spotify_access_endpoint = 'https://spotifysocialnetwork.firebaseio.com/users/.json?access_token='+gcp_access_token
        r = requests.get(spotify_access_endpoint)
        if r.status_code == 200:
            stringified = r.content.decode('utf8').replace("'", '"')
            allUsers = json.loads(stringified)
            print(allUsers)
        canFollow = {}
        try:
            for num,user_id in enumerate(allUsers):
                if user_id != _id:
                    canFollow[num] = allUsers[user_id]
        except:
            pass
    if request.method == 'POST':
        print('YEOOOO')
        spotify_access_endpoint = 'https://spotifysocialnetwork.firebaseio.com/users/.json?access_token='+gcp_access_token
        r = requests.get(spotify_access_endpoint)
        if r.status_code == 200:
            stringified = r.content.decode('utf8').replace("'", '"')
            allUsers = json.loads(stringified)
        canFollow = {}
        try:
            for num,user_id in enumerate(allUsers):
                if user_id != _id:
                    canFollow[num] = allUsers[user_id]
        except:
            pass
        for i in range(len(canFollow)):
            getFollow = request.POST.get(str(i))
            if getFollow:
                try:
                    following_endpoint = 'https://spotifysocialnetwork.firebaseio.com/users/'+_id+'/Following.json?access_token='+gcp_access_token
                    getFollowingReq = requests.get(following_endpoint)
                    stringified = getFollowingReq.content.decode('utf8').replace("'",'"')
                    existingFollowing = json.loads(stringified)
                    if isinstance(existingFollowing,list):
                        print('breh1')
                        existingFollowing += [getFollow]
                    else:
                        print('breh')
                        existingFollowing = [getFollow]
                    #print(existingFollowing)

                    following_body = {
                        'Following':existingFollowing
                    }
                    addFollowEndpoint = 'https://spotifysocialnetwork.firebaseio.com/users/'+_id+'.json?access_token='+gcp_access_token
                    addFollowReq = requests.patch(addFollowEndpoint,data=json.dumps(following_body))
                    #getFollowingReq = requests.get(addFollowEndpoint)
                    idOfUserFollowed = getId(getFollow)
                    print(addFollower(idOfUserFollowed,_id))
                    print(idOfUserFollowed)
                    #print(addFollowReq.content)
                except:
                    print('Something went wrong')
    return render(request,'users.html',context={'id':_id,'canFollow':canFollow,'canFollowLength':len(canFollow)})

def ShareView(request,_id):
    if request.method == 'GET':
        print(request.GET.get('link'))
        spotify_access_endpoint = 'https://spotifysocialnetwork.firebaseio.com/users/'+_id+'.json?access_token='+gcp_access_token
        r = requests.get(spotify_access_endpoint)
        recently_tracks = []
        if r.status_code == 200:
            stringified = r.content.decode('utf8').replace("'", '"')
            thisUser = json.loads(stringified)
        if thisUser:
            try:
                sp = spotipy.Spotify(auth=thisUser['spotify_access'])
                print(sp.current_user())
            except:
                token_endpoint = 'https://accounts.spotify.com/api/token'
                token_req_body = {
                    "grant_type": "refresh_token",
                    "refresh_token":thisUser['spotify_refresh']
                }
                token_req = requests.post(token_endpoint,data=token_req_body,headers=headers)
                token_response = json.loads(token_req.content.decode('utf8').replace("'", '"'))
                new_access_token = token_response["access_token"]
                sp = spotipy.Spotify(auth=new_access_token)
        if sp:
            recent_tracks = []
            recently_played = sp.current_user_recently_played()
            for track in recently_played['items']:
                this_track = track['track']
                #print('THIS TRACK\n',this_track)
                name = this_track['name']
                artist = this_track['artists'][0]['name']
                link = this_track['external_urls']['spotify']
                image = this_track['album']['images'][0]['url']
                data = {
                    "name":name,
                    "artist":artist,
                    "image":image,
                    "link":link
                }
                recent_tracks.append(data)
            #print(recent_tracks)
    if request.method == 'POST':
        song_id = request.POST.get('link').split('/')[-1]
        return redirect('create',link=song_id,uid=_id)
        # title = request.POST.get('title')
        # desc = request.POST.get('desc')
        # post_endpoint = 'https://spotifysocialnetwork.firebaseio.com/posts.json?access_token='+gcp_access_token
        # post_body = {
        #     "posterId":_id,
        #     "title":title,
        #     "desc":desc
        # }
        # createPost = requests.post(post_endpoint,data=json.dumps(post_body))
        #print(createPost.content)
        
    return render(request,'share.html',context={'recent_tracks':recent_tracks})

def createPostView(request,link,uid):
    if request.method == 'POST':
        title = request.POST.get('title')
        desc = request.POST.get('desc')
        post_endpoint = 'https://spotifysocialnetwork.firebaseio.com/posts.json?access_token='+gcp_access_token
        post_body = {
            "posterId":uid,
            "title":title,
            "desc":desc,
            "trackId":link
        }
        createPost = requests.post(post_endpoint,data=json.dumps(post_body))
        return HttpResponse('Created Post:{} with song id {}'.format(title,link))
    return render(request,'createpost.html',context={})

def getPosterFromId(_id):
    user_detail_endpoint = 'https://spotifysocialnetwork.firebaseio.com/users/'+_id+'.json?access_token='+gcp_access_token
    r = requests.get(user_detail_endpoint)
    stringified = r.content.decode('utf8').replace("'", '"')
    thisUser = json.loads(stringified)
    return thisUser['username']

def postDetailView(request,postId,uid):
    if request.method == 'GET':
        post_detail_endpoint = 'https://spotifysocialnetwork.firebaseio.com/posts/'+postId+'.json?access_token='+gcp_access_token
        r = requests.get(post_detail_endpoint)
        stringified = r.content.decode('utf8').replace("'", '"')
        thisPost = json.loads(stringified)
        postTitle = thisPost['title']
        desc = thisPost['desc']
        poster = getPosterFromId(thisPost['posterId'])
        if request.GET.get('like-btn'):
            return HttpResponse('Liked')

    if request.method == 'POST':
        if 'like-btn' in request.POST:
            post_likes_endpoint = 'https://spotifysocialnetwork.firebaseio.com/posts/'+postId+'/likes.json?access_token='+gcp_access_token
            post_likes_req = requests.get(post_likes_endpoint)
            stringified = post_likes_req.content.decode('utf8').replace("'",'"')
            post_likes = json.loads(stringified)
            if isinstance(post_likes,list):
                post_likes += [getPosterFromId(uid)]
            else:
                post_likes = [getPosterFromId(uid)]
            likes_body = {
                'likes':post_likes
            }
            print(likes_body)
            addLikeEndpoint = 'https://spotifysocialnetwork.firebaseio.com/posts/'+postId+'.json?access_token='+gcp_access_token
            addLikeReq = requests.patch(addLikeEndpoint,data=json.dumps(likes_body))
            print(addLikeReq.content)
            return HttpResponse('liked')
        else:
            comment = request.POST.get('comment')
            post_comments_endpoint = 'https://spotifysocialnetwork.firebaseio.com/posts/'+postId+'/comments.json?access_token='+gcp_access_token
            post_comments_req = requests.get(post_comments_endpoint)
            stringified = post_comments_req.content.decode('utf8').replace("'",'"')
            post_comments = json.loads(stringified)
            if isinstance(post_comments,list):
                post_comments += [{getPosterFromId(uid):comment}]
            else:
                post_comments = {getPosterFromId(uid):comment}
            comments_body = {
                'comments':post_comments
            }
            addCommentEndpoint = 'https://spotifysocialnetwork.firebaseio.com/posts/'+postId+'.json?access_token='+gcp_access_token
            addCommentReq = requests.patch(addCommentEndpoint,data=json.dumps(comments_body))
            print(addCommentReq.content)
            return HttpResponse('commented')

    return render(request,'postdetail.html',context={'title':postTitle,'desc':desc,'poster':poster})
