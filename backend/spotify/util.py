from .models import SpotifyToken
from django.utils import timezone
from datetime import timedelta
from .credentials import CLIENT_ID, CLIENT_SECRET
from requests import post, put, get

BASE_URL = "https://api.spotify.com/v1/"

# Retrieves SpotifyToken object associated with given session key (specific user)
def get_user_tokens(session_key):
    user_token = SpotifyToken.objects.filter(user=session_key)
    if user_token.exists():
        return user_token[0]
    else:
        return None

def update_or_create_user_token(session_key, access_token, refresh_token, token_type, expires_in):
    # token = SpotifyObject if token exists / = None if token doesn't exist
    token = get_user_tokens(session_key)
    expires_in = timezone.now() + timedelta(seconds=expires_in)

    # if token exists, update fields
    if token:
        token.access_token = access_token
        token.refresh_token = refresh_token
        token.expires_in = expires_in
        token.token_type = token_type
        token.save(update_fields=['access_token', 'refresh_token', 'token_type', 'expires_in'])
    # if not, create new SpotifyToken Object
    else:
        token = SpotifyToken(user=session_key, access_token=access_token, 
                             refresh_token=refresh_token, token_type=token_type, 
                             expires_in=expires_in)
        token.save()

# See if tokens exist in database with associated session key
def is_spotify_authenticated(session_key):
    tokens = get_user_tokens(session_key)
    if tokens:
        expiry = tokens.expires_in
        if expiry <= timezone.now():
            refresh_spotify_token(session_key)
        return True
    return False

def refresh_spotify_token(session_key):
    refresh_token = get_user_tokens(session_key).refresh_token
    response = post('https://accounts.spotify.com/api/token', data={
        'grant_type': 'refresh_token',
        'refresh_token': refresh_token,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET
    }).json()

    access_token = response.get('access_token')
    token_type = response.get('token_type')
    expires_in = response.get('expires_in')
    refresh_token = response.get('refresh_token')

    update_or_create_user_token(session_key, access_token, token_type, expires_in, refresh_token)

# handle any HTTP requests to Spotify API endpoints
def execute_spotify_api_request(session_key, endpoint, method='GET', data=None):
    tokens = get_user_tokens(session_key)
    headers = {'Content-Type': 'application/json', 'Authorization': "Bearer " + tokens.access_token}

    if method == 'POST':
        response = post(BASE_URL + endpoint, headers=headers, json=data)
    elif method == 'PUT':
        response = put(BASE_URL + endpoint, headers=headers, data=data)
    else:
        response = get(BASE_URL + endpoint, {}, headers=headers)
    try:
        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx and 5xx)
        return response.json()
    except Exception as e:
        return {'Error': f'Issue with request: {str(e)}'}
    
# Retrieves User ID -- needed to create new playlist
def get_user_id(session_key):
    endpoint = "me"
    user_profile = execute_spotify_api_request(session_key, endpoint)
    user_id = user_profile['id']
    return user_id

# Creates new playlist -- returns playlist id / external url
def create_new_playlist(session_key):
    user_id = get_user_id(session_key)
    endpoint = f"users/{user_id}/playlists"
    data = {
        'name': 'New Playlist', 
        'description': 'New Plyalist Created', 
        'public': False
        }
    response = execute_spotify_api_request(session_key=session_key, endpoint=endpoint, method='POST', data=data)
    playlist_id = response['id']
    playlist_url = response['external_urls']['spotify']
    return {"playlist_id": playlist_id, 'playlist_url': playlist_url}

# Retrieves and returns uris of recommended tracks based on given parameters (genres, artist, etc)
def get_recommendations(session_key):
    endpoint = "recommendations?seed_genres=k-pop%2Cpop"
    response = execute_spotify_api_request(session_key=session_key, endpoint=endpoint)
    track_uris = [track['uri'] for track in response['tracks']]
    return {"uris": track_uris}

# With plyalist id & recommended tracks uris, Creates new playlists -- returns playlist url
def create_playlist_and_add_tracks(session_key):
    new_playlist = create_new_playlist(session_key)
    recommended_track_uris = get_recommendations(session_key)

    endpoint = f"playlists/{new_playlist['playlist_id']}/tracks"
    data = recommended_track_uris

    response = execute_spotify_api_request(session_key=session_key, endpoint=endpoint, method='POST', data=data)
    if response:
        return new_playlist['playlist_url']