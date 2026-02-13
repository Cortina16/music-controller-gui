import websocket
import json
import threading
import time
import requests
import uuid
import logging
import asyncio


from . import access_token



class WebsocketInteract:

    def __init__(self, callback):
        self.token = asyncio.run(access_token.snipe_token())
        self.device_id = str(uuid.uuid4()).replace('-', '')
        self.wss_url = f"wss://guc3-dealer.spotify.com/?access_token="
        self.connection_id = None
        self.ws = None
        self.current_id = None
        self.callback = callback

        self.ws_headers = {"Origin": "https://open.spotify.com"}

    def register_device(self, connection_id):
        print(f"[*] Registering device {self.device_id} with Connection ID: {connection_id[:10]}...")

        url = f"https://guc-spclient.spotify.com/connect-state/v1/devices/{self.device_id}"

        headers = {
            "Authorization": f"Bearer {self.token}",
            "X-Spotify-Connection-Id": self.connection_id,
            "Content-Type": "application/json"
        }

        payload = {
            "member_type": "CONNECT_STATE",
            "device": {
                "device_info": {
                    "capabilities": {
                        "can_be_player": False,
                        "hidden": True
                    }
                }
            }
        }

        try:
            response = requests.put(url, headers=headers, json=payload)
            if response.status_code == 200:
                print("[+] Device registered successfully! You should start seeing updates.")
            else:
                print(f"[-] Registration failed: {response.status_code} {response.text}")
        except Exception as e:
            print(f"[-] Error registering: {e}")

    def _on_message(self, ws, message):
        data = json.loads(message)

        if "headers" in data and "Spotify-Connection-Id" in data["headers"]:
            self.connection_id = data["headers"]["Spotify-Connection-Id"]
            print(f"[!] Received Connection ID: {self.connection_id}")

            threading.Thread(target=self.register_device, args=(self.connection_id,)).start()

        elif "payloads" in data:
            for payload in data["payloads"]:
                if "cluster" in payload:
                    update_reason = payload["cluster"].get("update_reason")
                    if update_reason:
                        self._pass_out()
                    player_state = payload["cluster"].get("player_state", {})
                    track = player_state.get("track", {}).get("metadata", {})

                    if track:
                        print(f"\n[Now Playing] {track.get('title')} - {track.get('artist_name')}")
                        print(f"Paused: {player_state.get('is_paused')}")
        else:
            # Print other messages (pong, etc.)
            # print(message)
            pass
    def _pass_out(self):
        from spotify_handler import sp
        try:
            playback = sp.current_playback()

            if playback and playback.get('item'):
                new_id = playback['item']['id']

                if new_id != self.current_id:
                    self.current_id = new_id
                    print(f"🎵 New Track: {playback['item']['name']}")
                    a_list = [a["name"] for a in playback["item"]["artists"]]
                    self.callback(new_id, playback['progress_ms'], a_list, playback["item"]["name"])
            else:
                print("Waiting for active playback...")
        except Exception as e:
            print(e)

    def _on_open(self, ws):
        print("Connected to Spotify Dealer!")
        def run():
            while True:
                time.sleep(30)
                try:
                    ws.send(json.dumps({"type": "ping"}))
                except:
                    break
        threading.Thread(target=run, daemon=True).start()

    def _on_error(self, error, another_thing):
        logging.error(f"[-] Error: {error}, {another_thing} connection closed. Attempting to resuscitate...")
    def _on_close(self, close_status_code, close_msg):
        logging.warning(f"[-] Connection closed with status {close_status_code}, and message: {close_msg}. Attempting to resuscitate...")
    #     for i in range(10):
    #         self.ws = websocket.WebSocketApp(WSS_URL,
    #                                          header=self.headers,
    #                                          on_open=self.on_open,
    #                                          on_message=self.on_message,
    #                                          on_error=self.on_error,
    #                                          on_close=self.on_close)
    #         if self.ws.last_ping_tm > 3:
    #             return

    def run(self):
        retry_count = 0
        max_retries = 10

        self._pass_out()
        while retry_count < max_retries:
            logging.info(f"Connecting to Spotify (Attempt {retry_count + 1})...")

            self.ws = websocket.WebSocketApp(
                self.wss_url + self.token,
                header=self.ws_headers,
                on_open=self._on_open,
                on_message=self._on_message,
                on_error=self._on_error,
                on_close=self._on_close
            )

            self.ws.run_forever(ping_interval=30, ping_timeout=20)

            retry_count += 1
            wait_time = min(retry_count * 2, 30)
            logging.warning(f"Connection lost. Retrying in {wait_time}s...")
            time.sleep(wait_time)

        logging.error("Max retries reached. Giving up.")