from .models import SpotifyToken
from django.utils import timezone
from datetime import timedelta
from .credentials import CLIENT_ID, CLIENT_SECRET, REDIRECT_URI
from requests import Request, post, put, get
from django.http import HttpResponse, JsonResponse


BASE_URL = "https://api.spotify.com/v1/"

## 
class SpotifyUserAuth:
    def __init__(self, session_key):
        self.session_key = session_key
        self.tokens = self.get_user_tokens()
    
    def exchange_code_for_tokens(self, code):
        response = post('https://accounts.spotify.com/api/token', data={
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': REDIRECT_URI,    # needs to be the same redirect uri used in AuthURL
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET
        }).json()
        return response

    def get_user_tokens(self):
        user_tokens = SpotifyToken.objects.filter(user=self.session_key)
        if user_tokens.exists():
            return user_tokens.first()
        else:
            return None
    
    def update_or_create_user_token(self, access_token, refresh_token, token_type, expires_in):
        expires_in = timezone.now() + timedelta(seconds=expires_in)

        if self.tokens:
            self.tokens.access_token = access_token
            self.tokens.refresh_token = refresh_token
            self.tokens.token_type = token_type
            self.tokens.expires_in = expires_in
            self.tokens.save(update_fields=['access_token', 'refresh_token', 'token_type', 'expires_in'])
        else:
            self.tokens = SpotifyToken(
                user=self.session_key,
                access_token=access_token,
                refresh_token=refresh_token,
                token_type=token_type,
                expires_in=expires_in
            )
            self.tokens.save()

    def is_spotify_authenticated(self):
        if self.tokens:
            expiry = self.tokens.expires_in
            if expiry <= timezone.now():
                self.refresh_spotify_token()
            return True
        return False
    
    def refresh_spotify_token(self):
        refresh_token = self.tokens.refresh_token
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

        self.update_or_create_user_token(self.session_key, access_token, refresh_token, token_type, expires_in)
    
class Playlist:
    def __init__(self, session_key):
        self.session_key = session_key
        self.spotify_user = SpotifyUserAuth(session_key)

    ## Handle any HTTP requests to Spotify API endpoints
    def execute_spotify_api_request(self, endpoint, method='GET', data=None):
        tokens = self.spotify_user.tokens
        headers = {'Content-Type': 'application/json', 'Authorization': "Bearer " + tokens.access_token}

        if method == 'POST':
            response = post(BASE_URL + endpoint, headers=headers, json=data)
        elif method == 'PUT':
            response = put(BASE_URL + endpoint, headers=headers, json=data)
        else:
            response = get(BASE_URL + endpoint, {}, headers=headers)

        try:
            response.raise_for_status()  # Raise an HTTPError for bad responses (4xx and 5xx)
            return response.json()
        except Exception as e:
            return {'Error': f'Issue with request: {str(e)}'}
        
    def get_user_id(self):
        endpoint = "me"
        user_profile = self.execute_spotify_api_request(endpoint)
        user_id = user_profile['id']
        return user_id
    
    def create_new_playlist(self):
        user_id = self.get_user_id()
        endpoint = f"users/{user_id}/playlists"
        data = {'name': 'New Playlist', 'description': 'New Playlist Created', 'public': False}
        response = self.execute_spotify_api_request(endpoint, method='POST', data=data)
        playlist_id = response['id']
        playlist_url = response['external_urls']['spotify']
        return {"playlist_id": playlist_id, 'playlist_url': playlist_url}
    
    # right now, manually inputted genres but SHOULD be interactive
    ## can take genres / artists / tracks as seed params
    def get_recommendations(self):
        endpoint = endpoint = "recommendations?seed_genres=k-pop%2Cpop"
        response = self.execute_spotify_api_request(endpoint)
        track_uris = [track['uri'] for track in response['tracks']]
        return {"uris":track_uris}
    
    def create_playlist_and_add_tracks(self):
        new_playlist = self.create_new_playlist()
        recommended_track_uris = self.get_recommendations()

        endpoint = f"playlists/{new_playlist['playlist_id']}/tracks"
        response = self.execute_spotify_api_request(endpoint=endpoint, method='POST', data=recommended_track_uris)
        if response:
            return new_playlist['playlist_url']