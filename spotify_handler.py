import json
import os
import threading
import time

from flask.cli import load_dotenv
from spotipy.oauth2 import SpotifyClientCredentials, SpotifyOAuth
import spotipy




load_dotenv()
SCOPES = "user-read-playback-state user-read-currently-playing user-modify-playback-state"
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=os.getenv('SPOTIFY_CLIENT_ID'),
    client_secret=os.getenv('SPOTIFY_CLIENT_SECRET'),
    redirect_uri="http://127.0.0.1:8080",
    scope=SCOPES
))


def cover_photo(track_id):
    track = sp.track(track_id)
    print(track['album']['images'][0]['url'])
    return track['album']['images'][0]['url']


def get_important_information():
    while True:
        try:
            playback = sp.current_playback()

            if playback and playback.get('item'):
                packet = {
                    "artists" : [name["name"] for name in playback["item"]["artists"]]
                }
                return packet
            else:
                print('Waiting for active playback...')
        except Exception as e:
            print(e)
        time.sleep(2)


info = lambda x : threading.Thread(target=get_important_information).start()

get_important_information()



def skip():
    sp.next_track()


def previous_song():
    sp.previous_track()


def pause():
    sp.pause_playback()


def unpause():
    sp.start_playback()


def toggle_playback():
    try:
        playback = sp.current_playback()

        if playback and playback.get('item'):
            if playback['is_playing']:
                pause()
            else:
                unpause()
        else:
            print('Waiting for active playback...')
    except Exception as e:
        print(e)


class SpotifyListener(threading.Thread):
    def __init__(self, callback, ):
        super().__init__()
        self.callback = callback
        self.current_id = None
        self.daemon = True

    def run(self):
        while True:
            try:
                playback = sp.current_playback()

                if playback and playback.get('item'):
                    new_id = playback['item']['id']  # Use track ID, not album ID

                    if new_id != self.current_id:
                        self.current_id = new_id
                        print(f"🎵 New Track: {playback['item']['name']}")
                        self.callback(new_id, playback['progress_ms'])
                else:
                    print("Waiting for active playback...")
            except Exception as e:
                print(e)
            time.sleep(4)
