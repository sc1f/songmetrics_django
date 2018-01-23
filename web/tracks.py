import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

class TrackClient:
    def __init__(self, client_id: str, client_secret: str):
        """
        Initializes the client and a spotipy instance.
        :param client_id: client ID for Spotify API
        :param client_secret: client secret for Spotify API
        """
        if client_id is None:
            raise KeyError("Spotify client ID was not provided!")
        cred_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
        self.sp = spotipy.Spotify(client_credentials_manager=cred_manager)

    def getTracksByAlbum(self, query: str):
        """
        Returns all the tracks in a specific album. Assumes that query is for an album name, and returns the top result.
        :param query: the album you want to find.
        :return: list[dict] tracks in the album, no associated audio features
        """
        search = self.sp.search(q=query, limit=1, type='album')['albums']['items'][0]
        album_id = search['id']
        return self.sp.album_tracks(album_id=album_id)['items']

    def getTracksByArtist(self, query: str, sanitize: bool = True):
        """
        Given an artist name to query, returns all tracks by the artist with associated audio features.

        :param query: the artist you want to get tracks for
        :param sanitize: whether to remove compilation albums, live albums, and christmas albums (@sufjan stevens)
        :return: list[dict] - all tracks by the artist
        """
        artist_tracks = []
        search = self.sp.search(q=query, limit=1)['tracks']['items'][0]
        artist = search['artists'][0]

        if artist['name'].lower() != query.lower():
            raise KeyError("Artist name does not match queried name.")

        artist_albums = self.sp.artist_albums(artist_id=artist['id'], album_type='album')['items']  # we analyse only albums, no compilations/appearances

        for album in artist_albums:
            if sanitize:
                if len(album['artists']) > 1 or 'live' in album['name'].lower() or 'christmas' in album['name'].lower():
                    # skip anything with multiple artists, live, christmas - studio albums only
                    continue
            tracks = self.sp.album_tracks(album_id=album['id'])['items']
            for track in tracks:
                artist_data = {
                    'name': album['artists'][0]['name'],
                    'id': album['artists'][0]['id']
                }
                album_data = {
                    'name': album['name'],
                    'id': album['id'],
                    'image_url': album['images'][0]['url'] # default at 640 x 640
                }
                track['artists'] = artist_data
                track['album'] = album_data
                track['audio_features'] = self.sp.audio_features(track['id'])
                track['external_url'] = track['external_urls']['spotify']
                del track['disc_number']
                del track['available_markets']
                del track['preview_url']
                artist_tracks.append(track)

        return artist_tracks

    @staticmethod
    def serializeTracks(data: list):
        """
        Sanitizes track data for insertion into the database.
        :param data: list[dict] of tracks
        :return: data: list[dict] of tracks with audio features serialized
        """
        valid_features = ['danceability', 'energy', 'key', 'loudness', 'mode', 'speechiness', 'acousticness',
                          'instrumentalness', 'liveness', 'valence', 'tempo']
        for track in data:
            audio_features = track['audio_features'].items()
            for feature_name, feature_value in audio_features:
                if feature_name in valid_features:
                    track[feature_name] = feature_value

        return data

    @staticmethod
    def sortTracksByAudioFeature(feature, tracks):
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