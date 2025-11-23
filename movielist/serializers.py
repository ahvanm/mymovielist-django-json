from rest_framework import serializers
from movielist.models import *

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name']

class ListEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = ListEntry
        fields = ['id', 'user', 'movie_id', 'movie_title', 'rating', 'simplified_rating', 'date_watched', 'comments', 'poster_url']

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
    fav_film_count = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = FavPerson
        fields = ['id', 'user', 'person', 'person_name', 'profile_url', 'fav_film_count']
        read_only_fields = ['user', 'fav_film_count']
    
    def get_fav_film_count(self, obj):
        return obj.fav_persons.count()

class FavFilmsOfPersonSerializer(serializers.ModelSerializer):
    class Meta:
        model = FavFilmsOfPerson
        fields = ['id', 'favPerson', 'listEntry']

class FavFilmSerializer(serializers.ModelSerializer):
    class Meta:
        model = FavFilm
        fields = ['id', 'listEntry']