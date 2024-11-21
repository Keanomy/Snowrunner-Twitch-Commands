import base64
import hashlib
import json
import threading
from logging import Logger, getLogger
from typing import Any, Dict

from websocket import WebSocket

from config import Config


class OBS:

    def __init__(self) -> None:
        """Create a Websocket connection to OBS."""
        self.logger: Logger = getLogger("OBS.CLIENT")
        self.ws: WebSocket = None  # GET SOCKET BABABY!
        self.host: str = "localhost"
        self.port: int = 4455
        self.listener: OBS.Listener = None
        self.password: str = Config.get_config_key("OBS-WEBSOCKET-PASSWORD")
        self.url: str = f"ws://{self.host}:{self.port}"

    def connect(self):
        self.ws = WebSocket()
        try:
            self.ws.connect(self.url)  # TODO: ERROR CHECKING ConnectionRefusedError -> Reconnect?
        except ConnectionRefusedError:
            self.logger.debug("OBS not reachable.")
            print("OBS not reachable.")
            return

        self._auth()  # HANDLE AUTH

        self.listener = OBS.Listener(self.ws)
        self.listener.daemon = True
        self.listener.start()

    def _auth(self):
        reply: Dict[str, Any] = {
            "op": 1,
            "d": {
                "rpcVersion": 1,
            },
        }
        message: Dict[str, Any] = json.loads(self.ws.recv())  # GET AUTH DETAILS

        if message["d"]["authentication"]:
            salt: str = message["d"]["authentication"]["salt"]
            challenge: str = message["d"]["authentication"]["challenge"]
            secret = base64.b64encode(
                hashlib.sha256((self.password + salt).encode("utf-8")).digest()
            )
            auth = base64.b64encode(
                hashlib.sha256(secret + challenge.encode("utf-8")).digest()
            ).decode()
            auth = {
                "authentication": auth,
            }
        else:
            auth = {
                "authentication": "",
            }
        reply["d"].update(auth)
        # SEND IT
        self.ws.send(payload=json.dumps(reply))

    def close(self):
        self.listener.running = False
        self.ws.close()
        print("Shutting down OBS Websocket...")

    class Listener(threading.Thread):
        def __init__(self, ws: WebSocket):
            self.ws = ws
            self.logger: Logger = getLogger("OBS.LISTENER")
            self.running = True
            threading.Thread.__init__(self)

        def run(self):
            self.running = True
            self._listeningLoop()

        def _listeningLoop(self):
            while self.running:
                self.logger.debug(f"Received Event: {self.ws.recv()}")
