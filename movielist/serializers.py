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
    
class BioSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'bio']

class FavPersonSerializer(serializers.ModelSerializer):
    person_name = serializers.CharField(source='person.name', read_only=True)
    
    class Meta:
        model = FavPerson
        fields = ['id', 'user', 'person', 'person_name', 'profile_url']
        read_only_fields = ['user']

class FavFilmsOfPersonSerializer(serializers.ModelSerializer):
    class Meta:
        model = FavFilmsOfPerson
        fields = ['id', 'favPerson', 'listEntry']

class FavFilmSerializer(serializers.ModelSerializer):
    class Meta:
        model = FavFilm
        fields = ['id', 'listEntry']