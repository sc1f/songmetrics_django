from django.db import models
from .tracks import TrackClient

class Artist(models.Model):
    pass

class Album(models.Model):
    # A collection of Tracks
    pass

class Track(models.Model):
    # A single track, pulled from Spotify
    pass