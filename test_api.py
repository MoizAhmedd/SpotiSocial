import requests
import spotipy
import sys
import spotipy.util as util
from credentials import client_id,client_secret


scope = 'user-library-read,playlist-modify-public,user-modify-playback-state,user-library-modify,user-read-recently-played,user-follow-modify,user-read-currently-playing,user-follow-read,user-top-read'
username = 'moiz'
token = util.prompt_for_user_token(username, scope,client_id=client_id,client_secret=client_secret,redirect_uri='https://spotify.com')

#'https://www.spotify.com/ca-en/?code=AQCN1lDXCM-D0do3DdAMbIdSdsbcS9vZDWfR_i3xrM49I83YjiRxecYHQRAW3dOU3qh7f53n4X5tmOej4qRLhoambxkxCQORlYWnrxYqVgtYKNZlPq6Rd031nzJg6GbTTOfb-LCbABx-9q_Qj6Pp1TfFqKak63F_a5D0eh7C2n9LeWLq5Tt9lVG5t0-_aMuDDvIT6w7NA2E3gG1QM-g'
username2 = 'ahmed'
token2 = util.prompt_for_user_token(username2, scope,client_id=client_id,client_secret=client_secret,redirect_uri='https://spotify.com')
user2 = spotipy.Spotify(auth=token2)

def addTracks(artist,playlistID):
    results = sp.search(q='artist:'+artist,type='artist')
    items = results['artists']['items']
    artist_uri = items[0]['uri']
    tracks = sp.artist_top_tracks(artist_uri)
    for track in tracks['tracks']:
        track_id = [track['uri']]
        sp.user_playlist_add_tracks(username,playlistID,track_id)
        return 'Added' + track['name']


if token:
    sp = spotipy.Spotify(auth=token)
    #Test create playlist
    user_id = sp.current_user()['id']
    playlist = sp.user_playlist_create(user_id,'Adding Tracks..',public=True)
    #print(addTracks('NF',playlist['id']))
    print(sp.user_playlists(user_id))
else:
    print ("Can't get token for", username)
