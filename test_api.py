import requests
import spotipy
import sys
import json
import spotipy.util as util
from credentials import client_id,client_secret,apiKey,gcp_access_token


# scope = 'user-library-read,playlist-modify-public,user-modify-playback-state,user-library-modify,user-read-recently-played,user-follow-modify,user-read-currently-playing,user-follow-read,user-top-read'
# username = 'moiz'
# token = util.prompt_for_user_token(username, scope,client_id=client_id,client_secret=client_secret,redirect_uri='https://spotify.com')


# username2 = 'ahmed'
# token2 = util.prompt_for_user_token(username2, scope,client_id=client_id,client_secret=client_secret,redirect_uri='https://spotify.com')
# user2 = spotipy.Spotify(auth=token2)

def addTracks(artist,playlistID):
    results = sp.search(q='artist:'+artist,type='artist')
    items = results['artists']['items']
    artist_uri = items[0]['uri']
    tracks = sp.artist_top_tracks(artist_uri)
    for track in tracks['tracks']:
        track_id = [track['uri']]
        sp.user_playlist_add_tracks(username,playlistID,track_id)
        return 'Added' + track['name']


# if token:
#     pass
#     #sp = spotipy.Spotify(auth=token)
#     #print(sp.current_user())
#     #Test create playlist
#     #user_id = sp.current_user()['id']
#     #playlist = sp.user_playlist_create(user_id,'Adding Tracks..',public=True)
#     #print(addTracks('NF',playlist['id']))
#     #print(sp.user_playlists(user_id))
# else:
#     print ("Can't get token for", username)

#test_firebase
#endpoint = 'https://identitytoolkit.googleapis.com/v1/accounts:signUp?key='+apiKey
from google.oauth2 import service_account
import google
from google.auth.transport.requests import AuthorizedSession

# Define the required scopes
scopes = [
  "https://www.googleapis.com/auth/userinfo.email",
  "https://www.googleapis.com/auth/firebase.database"
]

# Authenticate a credential with the service account
credentials = service_account.Credentials.from_service_account_file(
    "spotifysocialnetwork-firebase-adminsdk-g88eg-a951c302ea.json", scopes=scopes)
# Use the credentials object to authenticate a Requests session.
authed_session = AuthorizedSession(credentials)

# Or, use the token directly, as described in the "Authenticate with an
# access token" section below. (not recommended)
request = google.auth.transport.requests.Request()
credentials.refresh(request)
access_token = credentials.token
#print(access_token)
endpoint = 'https://spotifysocialnetwork.firebaseio.com/users.json?access_token='+access_token
#specific_endpoint = 'https://spotifysocialnetwork.firebaseio.com/users/-Lsw2t_72aE_7Ndd64Vc.json?access_token='+access_token
r = requests.get(endpoint)
print(r.content)