## Spotify Metadata Reader (BETA)

(Probably best if you don't use this code unless you really know what it's doing - it's very buggy!)

### Purpose

This project reads track metadata from the Spotify Web API and publishes to CSV (will be Google Sheets). Currently,
the scope is user playlists only. Interface has not been developed, and is currently via command line argument (filth,
to be replaced)

This project makes use of the Spotipy library to hit the Spotify Web API. Read about both:
http://spotipy.readthedocs.io/en/latest/#
https://developer.spotify.com/web-api/


### Usage

Before using, you will need to create application credentials with at
https://developer.spotify.com/my-applications. Follow instructions, and make sure you set a redirect URI
then hit save. Populate config.ini.

Run `main.py` from command line with the following arguments:
 * username: your spotify username (credentials will be required)
 * request_type: one of "playlist", "playlists", or "all_playlists" (see reference)
 * playlist: name of target playlist. Only needed if using "playlist" request *** As of 04/08/2017 it's still
  necessary to run the code. That will change! ***


 On first run, follow the instructions in terminal for authorisation. You will need to grant permissions
 and copy your full redirect URL into the terminal to continue.

 e.g.

 `main.py "Jane Doe" "playlists" "Doesnt matter"` : this will return Jane Doe's playlists
 `main.py "Jane Doe" "playlist" "My First Playlist"` : this will return metadata for "My First Playlist"

 ### Reference

 ##### Request Types

 playlists:     Creates a CSV file in the project directory (sub-directory 'tests') containing a list of
                all of the authorised user's playlists (including private)
 playlist:      Creates a CSV file in the project directory (sub-directory 'tests') containing metadata
                for all tracks in the selected playlist
 all_playlists  AVOID! In development. Will create a single Google Sheet with one tab per playlist for all
                of the authorised user's playlist metadata

