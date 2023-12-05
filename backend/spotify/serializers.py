from rest_framework import serializers
from .models import Track

## Serialize Track objects to be returnable --> converts it to JSON objects
    # serializer = TrackSerializer(recommended_tracks, many=True)
    # return serializer.data
class TrackSerializer(serializers.Serializer):
    id = serializers.CharField(max_length=255)
    duration = serializers.IntegerField()