from request import Request
import sys


def main():

    if len(sys.argv) > 3:
        username = sys.argv[1]      # Mandatory
        request_type = sys.argv[2]  # Mandatory: playlists, playlist or all_playlists
        playlist = sys.argv[3]      # Mandatory if using playlist, ignored otherwise. Enter playlist name
        limit = sys.argv[4]         # Optional, only applicable to all_playlists. Limit playlists returned
        offset = sys.argv[5]        # Optional, only applicable to all_playlists. Start from the nth playlist
        print("")
        print("Searching playlists for user {}".format(sys.argv[1]))

    request = Request(request_type, username)
    request.send(playlist_name=playlist, limit=10)
    request.publish()

if __name__ == '__main__':
    main()
