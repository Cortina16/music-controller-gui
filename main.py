import requests
import queue
import io
import base64
import time
from dotenv import load_dotenv
from flask import Flask, request, jsonify, send_file, Response, json

import spotify_handler as spotify
import lyrics_handler

load_dotenv()
app = Flask(__name__)
update_queue = queue.Queue()


@app.route('/api/songs/<song_id>/lyrics', methods=['GET'])
def get_lyrics(song_id):
    data = lyrics_handler.get_song_lyrics(song_id)
    return jsonify(data)


@app.route('/api/songs/<song_id>/cover', methods=['GET'])
def get_cover(song_id):
    url = spotify.cover_photo(song_id)
    response = requests.get(url, stream=True)

    if response.status_code == 200:
        img_io = io.BytesIO(response.content)
        img_io.seek(0)
        return send_file(img_io, mimetype=response.headers.get('content-type'))
    else:
        return {"error": "Server could not fetch image"}, 500


@app.route('/api/songs/out-stream.json')
def unified_stream():
    def event_stream():
        while True:
            packet = update_queue.get()
            yield f"data: {json.dumps(packet)}\n\n"

    return Response(event_stream(), mimetype="text/event-stream")


@app.route('/api/songs/skip')
def skip_song():
    spotify.skip()
    {"Success"}, 200


@app.route('/api/songs/previous')
def previous_song():
    spotify.previous_song()


@app.route('/api/songs/pause')
def pause_playback():
    spotify.pause()
    return {"Success"}, 200


@app.route('/api/songs/unpause')
def unpause():
    spotify.unpause()
    return {"Success"}, 200
@app.route('/api/songs/toggle-playback')
def toggle_playback():
    spotify.toggle_playback()
    return {"Success"}, 200


def on_song_change(new_id, progress):
    lyrics = lyrics_handler.get_song_lyrics(new_id)
    with open("lyrics_out.json", "w") as file:
        json.dump(lyrics, file, indent=4)

    url = spotify.cover_photo(new_id)
    response = requests.get(url)

    if response.status_code == 200:
        base64_cover = base64.b64encode(response.content).decode('utf-8')
    else:
        base64_cover = None
    packet = {
        "song_id": new_id,
        "lyrics": lyrics,
        "progress": progress + time.time(),
        "base64_cover": base64_cover

    }
    update_queue.put(packet)


if __name__ == '__main__':
    lyrical_listener = spotify.SpotifyListener(on_song_change)
    lyrical_listener.start()

    app.run(debug=True, port=5000)
