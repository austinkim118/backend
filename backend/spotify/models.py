from django.db import models

# class SpotifyUser(models.Model):
#     session_key = models.CharField(max_length=50, unique=True)
#     username = models.CharField(max_length=50)
#     user_id = models.CharField(max_length=50)
                                   
# class SpotifyToken(models.Model):
#     user = models.OneToOneField(SpotifyUser, on_delete=models.CASCADE, primary_key=True)
#     created_at = models.DateTimeField(auto_now_add=True)
#     access_token = models.CharField(max_length=150)
#     token_type = models.CharField(max_length=150)
#     refresh_token = models.CharField(max_length=50)
#     expires_in = models.DateTimeField()

class SpotifyToken(models.Model):
    user = models.CharField(max_length=50, unique=True) # session key
    created_at = models.DateTimeField(auto_now_add=True)
    access_token = models.CharField(max_length=150)
    token_type = models.CharField(max_length=150)
    refresh_token = models.CharField(max_length=50)
    expires_in = models.DateTimeField()

class Track:
    def __init__(self, id, duration):
        self.id = id
        self.duration = duration