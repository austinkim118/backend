from django.shortcuts import render, redirect
from .credentials import CLIENT_ID, CLIENT_SECRET, REDIRECT_URI
from rest_framework.views import APIView
from requests import Request, post
from rest_framework import status
from rest_framework.response import Response
from .util import *
from django.http import HttpResponse, JsonResponse
import json

# get my app authenticated with Spotify, asking if we can have access to Spotify data for a specific user
# Then Spotify will say yes or no based on info i pass in.
# If yes, it will prompt the user to log in and agree to giving permission to my app to access data
# What kind of data the app will access specified in 'scope'
class AuthURL(APIView):
    def get(self, request, format=None):
        # the scopes depends on requirements -- google spotify api scopes
        scope = 'user-top-read playlist-modify-public playlist-modify-private user-read-private user-read-email'
        url = Request('GET', 'https://accounts.spotify.com/authorize', params={
            'scope': scope,
            'response_type': 'code',
            'redirect_uri': REDIRECT_URI,
            'client_id': CLIENT_ID
        }).prepare().url

        # this generates url which will lead user to authentication page, so have to redirect user
        # with the url this view is returning ==> after user logs in, it will redirec to 'spotify_callback'
        return Response({'url': url}, status=status.HTTP_200_OK)

# From above, the redirect uri will redirect to below function after user logs in
# Which will request for access/refresh token which will later allow the app to retrieve data
# The tokens are necessary when making API requests in the future
def spotify_callback(request, format=None):
    # retrieves authroization code from request
    code = request.GET.get('code')

    # sends POST request to spotify token endpoint to exchange auth code for access/refresh tokens
    response = post('https://accounts.spotify.com/api/token', data={
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': REDIRECT_URI,    # needs to be the same redirect uri used in AuthURL
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET
    }).json()

    # retrieves relevant info from response
    access_token = response.get('access_token')
    token_type = response.get('token_type')
    refresh_token = response.get('refresh_token')
    expires_in = response.get('expires_in')
    error = response.get('error')

    if error:
        # Handle the Spotify API error
        error_description = response.get('error_description', 'No error description provided.')
        return JsonResponse({'error': error, 'error_description': error_description})

    if not request.session.exists(request.session.session_key):
        request.session.create()

    update_or_create_user_token(request.session.session_key, access_token, refresh_token, token_type, expires_in)

    # redirec to front end
    react_callback_url = "http://localhost:3000/main"
    return redirect(react_callback_url)
        
# See if user is authenticated at login, if so skip Spotify Auth process
class IsAuthenticated(APIView):
    def get(self, request, format=None):
        is_authenticated = is_spotify_authenticated(self.request.session.session_key)
        return Response({'status': is_authenticated}, status=status.HTTP_200_OK)
    
# Retrieves top artists/tracks from user's account
class TopItems(APIView):
    def get(self, request, format=None):
        # Check if the session key is available
        if self.request.session.session_key:
            endpoint = "me/top/artists?"
            response = execute_spotify_api_request(self.request.session.session_key, endpoint)
            items = [{'name': item['name'], 'genres': item['genres']} for item in response['items']]
            return Response({'items': items}, status=status.HTTP_200_OK)
        else:
            # Handle the case where the session key is not available
            return Response({'error': 'Session key not found'}, status=status.HTTP_400_BAD_REQUEST)
        
## Requested by "Create Playlist" button in front end
## BUT should have POST method not Get -- from front end will be pushed User Inputs (Playlist length)
class CreatePlaylist(APIView):
    def get(self, request, format=None):
        session_key = self.request.session.session_key
        new_playlist_url = create_playlist_and_add_tracks(session_key)
        return Response({"url": new_playlist_url}, status=status.HTTP_200_OK)

class UserId(APIView):
    def get(self, request, format=None):
        session_key = self.request.session.session_key
        user = get_user_id(session_key)
        return Response(user)
    
class Recommendations(APIView):
    def get(self, request, format=None):
        session_key = self.request.session.session_key
        recommended_tracks = get_recommendations(session_key)
        return Response(recommended_tracks)