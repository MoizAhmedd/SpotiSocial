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
        scope = 'user-library-read,playlist-modify-public,user-modify-playback-state,user-library-modify,user-read-recently-played,user-follow-modify,user-read-currently-playing,user-follow-read,user-top-read'
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