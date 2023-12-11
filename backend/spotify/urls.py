from django.urls import path
# from .views import *
from .view import *

# urlpatterns = [
#     path('get-auth-url/', AuthURL.as_view()),
#     path('redirect/', spotify_callback),
#     path('is-authenticated/', IsAuthenticated.as_view()),
#     path('top-items/', TopItems.as_view()),
#     path('create-playlist/', CreatePlaylist.as_view()),
#     path('id/', UserId.as_view()),
#     path('recommendations/', Recommendations.as_view())
# ]

urlpatterns = [
    path('get-auth-url/', AuthURL.as_view()),
    path('redirect/', SpotifyCallback.as_view()),
    path('is-authenticated/', IsAuthenticated.as_view()),
    path('create-playlist/', CreatePlaylist.as_view()),
    path('id/', UserId.as_view()),
    path('recommendations/', Recommendations.as_view()),
    path('user-recommendations/', UserRecommendations.as_view()),
    path('recently-played/', RecentlyPlayed.as_view()),
    path('genres/', Genres.as_view()),
    path('username/', Username.as_view()),
]