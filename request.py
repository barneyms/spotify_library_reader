import spotipy
import spotipy.util as util
import pandas as pd
import os
import sys
import datetime
import numpy as np

import tools
import scopes
import library



class Request(object):

    def __init__(self, request_type, user_name, scope=None):

        self.scope = scope
        self.request_type = request_type
        self.token = None
        config = tools.get_config()
        self.client_id = config['clientid']
        self.client_secret = config['clientsecret']
        self.redirect = config['redirecturi']
        self.user_name = user_name
        self.auth = None
        self.user = None
        self.results = None

        if scope is None:
            if request_type in scopes.actions:
                self.scope = scopes.actions[request_type]
            else:
                raise ValueError('request type not allowed')

        token = util.prompt_for_user_token(
            self.user_name,
            self.scope,
            client_id=self.client_id,
            client_secret=self.client_secret,
            redirect_uri=self.redirect
            )
        print("")
        if token:
            self.auth = spotipy.Spotify(auth=token)
            print("successfully retrieved token for user {}".format(self.user_name))

        else:
            print("Can't get token for {}\n\n".format(self.user_name))
            self.auth = None

        try:
            self.user = User(self.auth, name=self.user_name)
        except ValueError:
            print('check user name...')

    def send(self, playlist_name=None, limit=10, offset=None):

        self.playlist = playlist_name
        if self.request_type == 'playlists':
            self.user.playlists = library.get_user_playlists(self)
            self.results = self.user.playlists
        elif self.request_type == 'playlist':
            if playlist_name is None:
                raise ValueError('No playlist name specified')
            if self.user.playlists is None:  # need playlist ids first
                self.user.playlists = library.get_user_playlists(self)
            else:
                pass
            playlist = library.Playlist(self, playlist_name)
            self.results = playlist.get()
        elif self.request_type == 'all_playlists':
            if self.user.playlists is None:  # need playlist ids first
                self.user.playlists = library.get_user_playlists(self)
            else:
                pass
            print('\n\n When using all_playlists request, results are published automatically.'
                  '\'publish\' method will not return results\n\n')

            for i, item in zip(range(limit+offset), self.user.playlists):
                if i >= offset:
                    self.playlist = self.user.playlists.iloc[i]['name']
                    playlist = library.Playlist(self, self.user.playlists.iloc[i]['name'])
                    self.results = playlist.get()
                    print('fetching playlist \"{}\"'.format(self.user.playlists.iloc[i]['name']))
                    self.publish()
            self.results = None  # results returned to empty to avoid re-publishing
            self.playlist = None

        else:
            print('sorry, this request isn\'t configured yet')

    def publish(self, google_auth=None):

        file_path = os.path.join(os.getcwd(), 'tests')
        now = datetime.datetime.now().strftime('%y%m%d_%H%M%S')
        uid = self.user_name.replace(' ', '').lower()
        if self.request_type == 'playlists':
            pid = self.request_type
        else:
            print(self.playlist)
            if self.playlist is None:
                pid = self.request_type
            else:
                pid = self.playlist.replace(' ', '').lower()
        file_name = uid + pid + now + '.csv'
        if self.results is not None:
            self.results.to_csv(os.path.join(file_path, file_name), index=False)

            sh = google_auth.open('Spotify Metadata')
            worksheet = sh.add_worksheet(title=self.playlist, rows="200", cols="30")
            worksheet = sh.worksheet(self.playlist)

            df = self.results

            # columns names
            columns = df.columns.values.tolist()
            # selection of the range that will be updated
            cell_list = worksheet.range('A1:' + tools.numberToLetters(len(columns)) + '1')
            # modifying the values in the range
            for cell in cell_list:
                val = columns[cell.col - 1]
                # if type(val) is str:
                #     val = val.decode('utf-8')
                cell.value = val
            # update in batch
            worksheet.update_cells(cell_list)

            # number of lines and columns
            num_lines, num_columns = df.shape
            # selection of the range that will be updated
            cell_list = worksheet.range('A2:' + tools.numberToLetters(num_columns) + str(num_lines + 1))
            # modifying the values in the range

            for cell in cell_list:
                val = df.iloc[cell.row - 2, cell.col - 1]
                # if type(val) is str:
                #     val = val.decode('utf-8')
                # if isinstance(val, (int, float, complex)):
                #     # note that we round all numbers
                #     val = int(round(val))
                cell.value = val
            # update in batch
            worksheet.update_cells(cell_list)

        # except AttributeError:
        #     print('Results set empty. Are you using the \"all_playlists\" method?')


class User(object):

    def __init__(self, auth, uid=None, name=None):
        self.user_name = name
        self.user_id = uid
        self.auth = auth
        self.user_data = None
        self.playlists = None

        if self.user_name is None and self.user_id is None:
            raise ValueError('no user name or id specified')
        elif self.user_id is None:
            self.user_data = auth.me()
            self.user_id = self.user_data['id']




