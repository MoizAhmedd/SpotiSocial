from django.shortcuts import render
from django.http import HttpResponse, HttpRequest
from credentials import client_id,client_secret
from django.views.generic import TemplateView
import spotipy
import sys
import spotipy.util as util

# Create your views here.
class LoginView(TemplateView):
    def get(self,request,*args,**kwargs):
        scope = 'user-library-read,playlist-modify-public,user-modify-playback-state,user-library-modify,user-read-recently-played,user-follow-modify,user-read-currently-playing,user-follow-read,user-top-read'
        username = request.GET.get('uname')
        token = util.prompt_for_user_token('tester', scope,client_id=client_id,client_secret=client_secret,redirect_uri='http://localhost:8000/authorize')
        return render(request,'login.html',context={})

class AuthorizeView(TemplateView):
    template_name = 'authorize.html'