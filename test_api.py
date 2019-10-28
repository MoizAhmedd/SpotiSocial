import requests
import spotipy
import sys
import spotipy.util as util
from credentials import client_id,client_secret


scope = 'user-library-read'
username = 'moiz'
token = util.prompt_for_user_token(username, scope,client_id=client_id,client_secret=client_secret,redirect_uri='https://spotify.com')

#'https://www.spotify.com/ca-en/?code=AQCN1lDXCM-D0do3DdAMbIdSdsbcS9vZDWfR_i3xrM49I83YjiRxecYHQRAW3dOU3qh7f53n4X5tmOej4qRLhoambxkxCQORlYWnrxYqVgtYKNZlPq6Rd031nzJg6GbTTOfb-LCbABx-9q_Qj6Pp1TfFqKak63F_a5D0eh7C2n9LeWLq5Tt9lVG5t0-_aMuDDvIT6w7NA2E3gG1QM-g'


if token:
    sp = spotipy.Spotify(auth=token)
    results = sp.current_user()
    print(results)
    print(sp.recommendation_genre_seeds())
else:
    print ("Can't get token for", username)