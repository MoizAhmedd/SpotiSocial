from django.shortcuts import render,redirect
from django.http import HttpResponse, HttpRequest
from credentials import client_id,client_secret,headers
from django.views.generic import TemplateView
import spotipy
import sys
import spotipy.util as util
import requests

# Create your views here.
class LoginView(TemplateView):
    def get(self,request,*args,**kwargs):
        scope = 'user-library-read,playlist-modify-public,user-modify-playback-state,user-library-modify,user-read-recently-played,user-follow-modify,user-read-currently-playing,user-follow-read,user-top-read'
        #username = request.GET.get('uname')
        url = 'https://accounts.spotify.com/authorize?response_type=code&client_id='+client_id+'&scope='+scope+'&redirect_uri=http://localhost:8000/authorize&state=Ggt7OnxNBIX1YN4R'
        return redirect(url)
        #token = util.prompt_for_user_token('tester', scope,client_id=client_id,client_secret=client_secret,redirect_uri='http://localhost:8000/authorize')

class AuthorizeView(TemplateView):
    def get(self,request,*args,**kwargs):
        code = request.GET.get('code','')
        auth_body = {
            'grant_type':'authorization_code',
            'code':code,
            'redirect_uri':'http://localhost:8000/authorize'
        }
        headers = headers
        auth_request = requests.post('https://accounts.spotify.com/api/token',data=auth_body,headers=headers)
        print(auth_request.content)
        return render(request,'authorize.html',context={})