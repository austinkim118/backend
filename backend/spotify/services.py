from .models import SpotifyToken
from django.utils import timezone
from datetime import timedelta
from .credentials import CLIENT_ID, CLIENT_SECRET, REDIRECT_URI
from requests import post, put, get
from collections import Counter

BASE_URL = "https://api.spotify.com/v1/"

class SpotifyUser:
    """Authenticates Spotify User"""
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
    """Operations regarding generating Spotify Playlist"""
    def __init__(self, session_key):
        self.session_key = session_key
        self.user = SpotifyUser(session_key)

    ## Handle any HTTP requests to Spotify API endpoints
    def execute_spotify_api_request(self, endpoint, method='GET', data=None):
        tokens = self.user.tokens
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
        """
        :return (str): Spotify User Id
        """
        endpoint = "me"
        user_profile = self.execute_spotify_api_request(endpoint)
        user_id = user_profile['id']
        return user_id
    
    def create_new_playlist(self, id):
        """
        :param (str): Spotify User Id
        :return Json{playlist_id, playlist_url}
        """
        endpoint = f"users/{id}/playlists"
        data = {'name': 'New Playlist', 'description': 'New Playlist Created', 'public': False}
        response = self.execute_spotify_api_request(endpoint, method='POST', data=data)
        playlist_id = response['id']
        playlist_url = response['external_urls']['spotify']
        return {"playlist_id": playlist_id, 'playlist_url': playlist_url}
    
    # right now, manually inputted genres but SHOULD be interactive
    ## can take genres / artists / tracks as seed params
    def get_recommendations(self, seed):
        """
        :param seed (list[str]): Up to 5 seed parameters - can be genre/artist/track ==> but for now, will be genres
        """
        ## market should be based on user not hard coded
        ## limit should be based on duration inputted by user
        ## ==> 30min = 20 tracks, 1hr == 40 tracks, etc.
        endpoint = f"recommendations?limit=30&market=US&seed_genres={seed[0]}%2C{seed[1]}%2C+{seed[2]}"
        response = self.execute_spotify_api_request(endpoint)
        track_uris = [track['uri'] for track in response['tracks']]
        return {"uris": track_uris}
    
    def create_playlist_and_add_tracks(self, playlist, uris):
        """
        :param playlist (json): json object {id, url} -- newly created empty playlist
        :param uris (list[str]): json object {uri: list of track uri strings} -- uris of recommended tracks
        """
        endpoint = f"playlists/{playlist['playlist_id']}/tracks"
        response = self.execute_spotify_api_request(endpoint, method='POST', data=uris)
        if response:
            return playlist['playlist_url']
        
    def get_recently_played_artists(self):
        """
        :return ids_string (str): Artist ids in a single string separated by commas
        """
        endpoint = "me/player/recently-played?limit=50"
        response = self.execute_spotify_api_request(endpoint)
        ## grabbed only the first artist named for each track -- b/c number of artists must be <= 50
        artist_ids = [item['track']['artists'][0]['id'] for item in response['items']]
        # artist_ids = [artist['id'] for item in response['items'] for artist in item['track']['artists']]
        ids_string = ",".join(artist_ids)
        return ids_string
    
    def get_artist_genres(self, ids):
        """
        :param ids (str): Artist ids separated by commac no space
        :return genre_counts list(tuple): list of tuples (genre name, count) from most common to least
        """
        endpoint = f"artists?ids={ids}"
        response = self.execute_spotify_api_request(endpoint)
        genres = [genre for artist in response['artists'] for genre in artist['genres']]

        # returns list of tuples -- [[item, count]]
        genre_counts = Counter(genres).most_common()
        return {'genres': genre_counts}