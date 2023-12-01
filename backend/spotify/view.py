from django.shortcuts import render, redirect
from .credentials import CLIENT_ID, CLIENT_SECRET, REDIRECT_URI
from rest_framework.views import APIView
from requests import Request
from rest_framework import status
from rest_framework.response import Response
from .services import SpotifyUser, Playlist

class AuthURL(APIView):
    def get(self, request, format=None):
        scope = 'user-top-read playlist-modify-public playlist-modify-private user-read-private user-read-email'
        url = Request('GET', 'https://accounts.spotify.com/authorize', params={
            'scope': scope,
            'response_type': 'code',
            'redirect_uri': REDIRECT_URI,
            'client_id': CLIENT_ID
        }).prepare().url
        return Response({'url': url}, status=status.HTTP_200_OK)

class SpotifyCallback(APIView):
    def get(self, request, format=None):
        # retrieve auth code from request(the URI)
        code = request.GET.get('code')

        # Manually create session key
        if not request.session.exists(request.session.session_key):
            request.session.create()

        spotify_user = SpotifyUser(request.session.session_key)

        # sends POST request to spotify token endpoint to exchange auth code for access/refresh tokens
        response = spotify_user.exchange_code_for_tokens(code)

        # retrieves relevant info from the response
        access_token = response.get('access_token')
        token_type = response.get('token_type')
        refresh_token = response.get('refresh_token')
        expires_in = response.get('expires_in')
        error = response.get('error')

        if error:
            # Handle the Spotify API error
            error_description = response.get('error_description', 'No error description provided.')
            return Response({'error': error, 'error_description': error_description}, status=status.HTTP_400_BAD_REQUEST)

        # creates or updates the user token
        spotify_user.update_or_create_user_token(access_token, refresh_token, token_type, expires_in)

        # redirect to the front end
        react_callback_url = "http://localhost:3000/main"
        return redirect(react_callback_url)
        
class IsAuthenticated(APIView):
    def get(self, request, format=None):
        spotify_user = SpotifyUser(request.session.session_key)
        is_authenticated = spotify_user.is_spotify_authenticated()
        return Response({'status': is_authenticated}, status=status.HTTP_200_OK)

class CreatePlaylist(APIView):
    def get(self, request, format=None):
        playlist = Playlist(request.session.session_key)
        new_playlist_url = playlist.create_playlist_and_add_tracks()
        return Response({"url": new_playlist_url}, status=status.HTTP_200_OK)

class UserId(APIView):
    def get(self, request, format=None):
        spotify_user = Playlist(request.session.session_key)
        user_id = spotify_user.get_user_id()
        return Response({'user_id': user_id}, status=status.HTTP_200_OK)

class Recommendations(APIView):
    def get(self, request, format=None):
        playlist = Playlist(request.session.session_key)
        recommended_tracks = playlist.get_recommendations()
        return Response(recommended_tracks, status=status.HTTP_200_OK)