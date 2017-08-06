import spotipy
import spotipy.util as util
import sys
import pandas as pd
import os
import datetime

import tools
from tools import DefaultList

# THIS CODE IS DEPRECATED. TRIGGER USING MAIN.PY

scope = 'playlist-read-private'
# choose_playlist = "Love, Death and The Open Road"


def authorise(scopes=None):

    config = tools.get_config()
    client_id = config['clientid']
    client_secret = config['clientsecret']
    redirect = config['redirecturi']

    if len(sys.argv) > 2:
        username = sys.argv[1]
        choose_playlist = sys.argv[2]
        print("")
        print("Searching playlists for user {}".format(sys.argv[1]))
    else:
        print("To run, enter Spotify username, e.g. {} \"Joe Bloggs\"".format(sys.argv[0]))
        sys.exit()

    token = util.prompt_for_user_token(
        username,
        scopes,
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri=redirect
        )
    print("")
    if token:
        sp = spotipy.Spotify(auth=token)
        print("successfully retrieved token for user {}".format(username))

    else:
        print("Can't get token for {}\n\n".format(username))
        sp = None
    return sp, username, choose_playlist


def get_me(spoty):
    """
    Get's current authorised user's username

    :param spoty: authorisation token
    :return: user id for authorised user
    """

    me = spoty.me()
    return me['id']


def get_playlists(spoty, user_id):
    """
    Gets a list of all of the authorised user's playlists, inc private

    :param spoty: authorisation token
    :param user_id:
    :param choose_playlist:
    :return: dataframe containing playlist summary data
    """

    playlists = spoty.user_playlists(user_id, limit=50)

    my_playlists = DefaultList([])
    for i, playlist in enumerate(playlists['items']):

        if playlist['tracks']['total'] != '0':

            this_playlist = {}
            this_playlist['playlist_id'] = playlist['id']
            this_playlist['name'] = playlist['name']
            this_playlist['total_tracks'] = playlist['tracks']['total']
            this_playlist['public'] = playlist['public']
            this_playlist['url'] = playlist['external_urls']['spotify']

            my_playlists[i] = this_playlist

    df = pd.DataFrame.from_dict(my_playlists)

    return df


def get_a_playlist(spoty, user_id, playlists, choose_playlist):

    tracks = DefaultList([])

    index = playlists[playlists['name'] == choose_playlist].index.values.tolist()
    ix = index[0]

    print('playlist name: {0}; id: {1}; total tracks: {2}'.format(
        playlists['name'][ix], playlists['playlist_id'][ix], playlists['total_tracks'][ix]))
    target = playlists['playlist_id'][ix]

    results = spoty.user_playlist(user_id, target,
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

        tracks[i] = dtc
    return tracks


def get_metadata(tracks, spoty):
    outside_track_list = chunks(tracks, 15)
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

        album_meta = album_info(spoty, album_ids)
        for i, track in enumerate(tracks):
            track['ReleaseDate'] = album_meta['albums'][i]['release_date']
            track['RecordLabel'] = album_meta['albums'][i]['label']

        # Get artist details
        artist_meta = artist_info(spoty, artist_ids)
        for i, track in enumerate(tracks):
            try:   # tags will always refer to first artist listed
                tags = '; '.join(artist_meta['artists'][i]['genres'][:4])
                track['ArtistTags'] = tags
            except IndexError:
                track['ArtistTags'] = 'none'

        feature_meta = features_info(spoty, track_ids)

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

    column_order = ('Title'
                    , 'Album'
                    , 'Artist'
                    , 'ArtistTags'
                    , 'ReleaseDate'
                    , 'RecordLabel'
                    , 'Comments'
                    , 'TrackId'
                    , 'AlbumId'
                    , 'ArtistId'
                    , 'acousticness'
                    , 'danceability'
                    , 'energy'
                    , 'instrumentalness'
                    , 'key'
                    , 'liveness'
                    , 'loudness'
                    , 'mode'
                    , 'speechiness'
                    , 'tempo'
                    , 'valence')

    main_df = main_df.ix[:, column_order]

    return main_df


def album_info(spoty, album_ids):

    album = spoty.albums(albums=album_ids)

    # print(album)
    # print('')
    return album


def artist_info(spoty, artist_ids):

    artist = spoty.artists(artists=artist_ids)

    return artist


def features_info(spoty, track_ids):

    track_features = spoty.audio_features(tracks=track_ids)

    return track_features


def chunks(l, n):
    # For item i in a range that is a length of l,
    for i in range(0, len(l), n):
        # Create an index range for l of n items:
        yield l[i:i+n]


if __name__ == '__main__':

    spotify, username, playlist_name = authorise(scope)

    me = get_me(spotify)

    my_playlists = get_playlists(spotify, me)

    playlist_dict = get_a_playlist(spotify, me, my_playlists, playlist_name)

    metadata = get_metadata(playlist_dict, spotify)

    now = datetime.datetime.now().strftime('%y%m%d_%H%M%S')

    metadata.to_csv(os.path.join(os.getcwd(), 'tests', 'sample_{}.csv'.format(now)), index=False)

