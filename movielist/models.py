from django.db import models

# Create your models here.
class User(models.Model):
    username = models.CharField(max_length=255, unique=True)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    bio = models.TextField(null = True)

    def __str__(self) -> str:
        return str(self.username)

    class Meta:
        indexes = [
            models.Index(fields=['username'])
        ]
        ordering = ['username', 'first_name', 'last_name']


class ListEntry(models.Model):
    user = models.ForeignKey('User', on_delete = models.CASCADE)
    movie_id = models.CharField(max_length=255)
    movie_title = models.CharField(max_length=255, null = True)
    rating = models.DecimalField(decimal_places = 1, max_digits = 3)
    date_watched = models.DateField(null = True)
    comments = models.TextField(null = True)
    poster_url = models.CharField(max_length=255, null = True)

    def __str__(self) -> str:
        return f"{self.user.username}: '{self.movie_id}'"

    class Meta:
        indexes = [
            models.Index(fields=['user', 'movie_id'])
        ]


class Person(models.Model):
    id = models.CharField(max_length=255, primary_key=True)
    name = models.CharField(max_length=255)

    def __str__(self) -> str:
        return f"({self.name}: '{self.id})'"
    
    class Meta:
        indexes = [
            models.Index(fields=['id', 'name'])
        ]


class AssociatedWith(models.Model):
    person = models.ForeignKey(Person, on_delete = models.CASCADE)
    movie_id = models.CharField(max_length=255)

    def __str__(self) -> str:
        return f"(Movie {self.movie_id}: '{self.person})'"
    
    class Meta:
        indexes = [
            models.Index(fields=['person', 'movie_id'])
        ]