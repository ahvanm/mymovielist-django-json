from rest_framework import serializers
from movielist.models import *

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name']

class ListEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = ListEntry
        fields = ['id', 'user', 'movie_id', 'movie_title', 'rating', 'date_watched', 'comments', 'poster_url']

class EntryIDSerializer(serializers.ModelSerializer):
    class Meta:
        model = ListEntry
        fields = ['id', 'movie_id', 'movie_title']