import spotipy
import spotipy.util as util
import pandas as pd
import os
import sys

import tools
from tools import chunks


class Playlist(object):

    def __init__(self, request, playlist_name):
        self.name = playlist_name
        self.user = request.user
        self.id = None
        self.credentials = request.auth
        self.tracks_json = tools.DefaultList([])
        self.metadata = None

        df = self.user.playlists
        index = df[df['name'] == self.name].index.values.tolist()
        ix = index[0]
        self.id = df['playlist_id'][ix]
        self.track_count = df['total_tracks'][ix]
        print('playlist name: {0}; id: {1}; total tracks: {2}'.format(
            df['name'][ix], self.id, self.track_count))

    def get(self):

        results = self.credentials.user_playlist(self.user.user_id, self.id,
                                                 fields="tracks,next")

        for i, item in enumerate(results['tracks']['items']):
            dtc = {}
            dtc['Title'] = item['track']['name']
            dtc['TrackId'] = item['track']['id']
            dtc['Album'] = item['track']['album']['name']
            dtc['AlbumId'] = item['track']['album']['id']
            dtc['Comments'] = ''
            try:
                dtc['Artist'] = item['track']['album']['artists'][0]['name']
            except IndexError:
                dtc['Artist'] = 'none'
            try:  # only take first artist ID
                dtc['ArtistId'] = item['track']['album']['artists'][0]['id']
            except IndexError:
                dtc['ArtistId'] = 'none'

            self.tracks_json[i] = dtc

        outside_track_list = chunks(self.tracks_json, 20)  # this is to avoid hitting the API id count limit

        for j, tracks in enumerate(outside_track_list):

            track_ids = []
            for track in tracks:
                track_ids.append(track['TrackId'])

            artist_ids = []
            for track in tracks:
                artist_ids.append(track['ArtistId'])

            album_ids = []
            for track in tracks:
                album_ids.append(track['AlbumId'])

            # get album details
            album_meta = self.credentials.albums(albums=album_ids)
            for i, track in enumerate(tracks):
                track['ReleaseDate'] = album_meta['albums'][i]['release_date']
                track['RecordLabel'] = album_meta['albums'][i]['label']

            # Get artist details
            artist_meta = self.credentials.artists(artists=artist_ids)
            for i, track in enumerate(tracks):
                try:  # tags will always refer to first artist listed
                    tags = '; '.join(artist_meta['artists'][i]['genres'][:4])
                    track['ArtistTags'] = tags
                except IndexError:
                    track['ArtistTags'] = 'none'

            # get track features data
            feature_meta = self.credentials.audio_features(tracks=track_ids)
            for i, track in enumerate(tracks):
                track['danceability'] = feature_meta[i]['danceability']
                track['energy'] = feature_meta[i]['energy']
                track['key'] = feature_meta[i]['key']
                track['loudness'] = feature_meta[i]['loudness']
                track['mode'] = feature_meta[i]['mode']
                track['speechiness'] = feature_meta[i]['speechiness']
                track['acousticness'] = feature_meta[i]['acousticness']
                track['instrumentalness'] = feature_meta[i]['instrumentalness']
                track['liveness'] = feature_meta[i]['liveness']
                track['valence'] = feature_meta[i]['valence']
                track['tempo'] = feature_meta[i]['tempo']

            if j == 0:
                main_df = pd.DataFrame.from_dict(tracks)

            else:
                sub_df = pd.DataFrame.from_dict(tracks)
                main_df = main_df.append(sub_df)

        column_order = ('Title', 'Album', 'Artist', 'ArtistTags', 'ReleaseDate', 'RecordLabel'
                        , 'Comments', 'TrackId', 'AlbumId', 'ArtistId' , 'acousticness', 'danceability'
                        , 'energy', 'instrumentalness', 'key', 'liveness', 'loudness', 'mode'
                        , 'speechiness', 'tempo', 'valence')

        main_df = main_df.ix[:, column_order]
        return main_df


def get_user_playlists(request):
    """
    Gets a list of all of the authorised user's playlists, inc private

    :param spoty: authorisation token
    :param user_id:
    :param choose_playlist:
    :return: dataframe containing playlist summary data
    """

    playlists = request.auth.user_playlists(request.user.user_id, limit=50)

    my_playlists = tools.DefaultList([])
    for i, playlist in enumerate(playlists['items']):

        if playlist['tracks']['total'] != 0:
            this_playlist = {}
            this_playlist['playlist_id'] = playlist['id']
            this_playlist['name'] = playlist['name']
            this_playlist['total_tracks'] = playlist['tracks']['total']
            this_playlist['public'] = playlist['public']
            this_playlist['url'] = playlist['external_urls']['spotify']

            my_playlists[i] = this_playlist

    df = pd.DataFrame.from_dict(my_playlists)

    return df



