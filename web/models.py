from django.db import models

class Artist(models.Model):
    name = models.CharField(max_length=255, null=False)
    spotify_id = models.CharField(max_length=255, null=False, unique=True)

    def __str__(self):
        return self.name

class Album(models.Model):
    # A collection of Tracks
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE)
    name = models.CharField(max_length=255, null=False)
    spotify_id = models.CharField(max_length=255, null=False, unique=True)
    image_url = models.URLField(max_length=255, null=False)

    def __str__(self):
        return self.name

class Track(models.Model):
    # A single track, pulled from Spotify
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE)
    album = models.ForeignKey(Album, on_delete=models.CASCADE)
    name = models.CharField(max_length=255, null=False)
    spotify_id = models.CharField(max_length=255, null=False, unique=True)
    spotify_uri = models.CharField(max_length=255, null=False)
    external_url = models.URLField()
    track_number = models.IntegerField()
    duration = models.BigIntegerField()
    type = models.CharField(max_length=255)
    explicit = models.BooleanField()
    # begin audio features
    danceability = models.FloatField()
    energy = models.FloatField()
    key = models.FloatField()
    loudness = models.FloatField()
    mode = models.FloatField()
    speechiness = models.FloatField()
    acousticness = models.FloatField()
    instrumentalness = models.FloatField()
    liveliness = models.FloatField()
    valence = models.FloatField()
    tempo = models.FloatField()
    time_signature = models.FloatField()

    def __str__(self):
        return self.name
