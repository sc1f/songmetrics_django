import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

class TrackClient:
    def __init__(self, client_id: str, client_secret: str):
        if client_id is None:
            raise KeyError("Spotify client ID was not provided!")
        cred_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
        self.sp = spotipy.Spotify(client_credentials_manager=cred_manager)

    def getAllTracksByAlbum(self, query):
        search = self.sp.search(q=query, limit=1, type='album')['albums']['items'][0]
        album_id = search['id']
        return self.sp.album_tracks(album_id=album_id)['items']

    def getAllTracksByArtist(self, query):
        # todo: optimize
        artist_tracks = []
        search = self.sp.search(q=query, limit=1)['tracks']['items'][0]
        artist = search['artists'][0]

        if artist['name'].lower() != query.lower():
            raise KeyError("Artist name does not match queried name.")

        artist_albums = self.sp.artist_albums(artist_id=artist['id'], album_type='album')[
            'items']  # we analyse only albums, no compilations/appearances

        for album in artist_albums:
            if len(album['artists']) > 1:
                # skip anything with multiple artists - Planetarium, etc.
                continue
            tracks = self.sp.album_tracks(album_id=album['id'])['items']
            for track in tracks:
                track['album'] = album # manually set album
                artist_tracks.append(track)

        return artist['id'], artist['name'], artist_tracks

    def getAudioFeaturesForTracks(self, tracks):
        # todo optimize
        for t in tracks:
            t['audio_features'] = self.sp.audio_features(t['id'])[0]
        return tracks

    def sortTracksByAudioFeature(self, feature, tracks):
        track_features = []
        valid_features = ['danceability', 'energy', 'key', 'loudness', 'mode', 'speechiness', 'acousticness',
                          'instrumentalness', 'liveness', 'valence', 'tempo']
        if feature not in valid_features:
            raise IndexError("You didn't query a valid feature!")
        # pluck specified feature and sort in one pass
        for track in tracks:
            meta = {
                'selected_feature': feature,
                'feature_value': track[feature],
                'name': track['name']
            }
            track_features.append(meta)
        track_features.sort(key=lambda t: t['feature_value'])
        return track_features