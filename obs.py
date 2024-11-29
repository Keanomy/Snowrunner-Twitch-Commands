import base64
import hashlib
import json
import os
import threading
from logging import Logger, getLogger
from typing import Any, Dict

from websocket import WebSocket


class OBS:

    def __init__(self) -> None:
        """Create a Websocket connection to OBS."""
        self.logger: Logger = getLogger("OBS.CLIENT")
        self.request_id = 0
        self.ws: WebSocket = None
        self.host: str = "localhost"
        self.port: int = 4455
        self.listener: OBS.Listener = None
        self.password: str = os.environ.get("OBS_WS_PASS")
        self.url: str = f"ws://{self.host}:{self.port}"

    def connect(self):
        self.ws = WebSocket()
        try:
            self.ws.connect(self.url)  # TODO: ERROR CHECKING ConnectionRefusedError -> Reconnect?
        except ConnectionRefusedError:
            self.logger.debug("OBS not reachable.")
            print("OBS not reachable.")
            return

        self._auth()

        self.listener = OBS.Listener(self.ws)
        self.listener.daemon = True
        self.listener.start()

    def _auth(self):
        reply: Dict[str, dict] = {
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

    def call(self, request: dict[str, dict]) -> None:
        payload: Dict[str, dict] = {"op": 6, "d": request}
        self.request_id += 1
        payload["d"].update({"requestId": self.request_id})
        request_event: threading.Event = threading.Event()
        self.listener._request_tracker[self.request_id] = request_event
        self.ws.send(payload=json.dumps(payload))
        request_event.wait(30)
        self.listener._request_tracker.pop(self.request_id)
        reply = self.listener._request_replies.pop(self.request_id)
        return reply

    def close(self):
        self.listener.running = False
        self.ws.close()
        print("Shutting down OBS Websocket...")

    def SetSourceFilterEnabled(self, filter_name: str, source_name: str, visibility: bool = True):
        request: {str, dict} = {
            "requestType": "SetSourceFilterEnabled",
            "requestData": {
                "sourceName": source_name,
                "filterName": filter_name,
                "filterEnabled": visibility,
            },
        }
        self.call(request)

    def SetSceneItemEnabled(self, scene_name: str, source_name: str, visibility: bool = True):
        request: {str, dict} = {
            "requestType": "SetSceneItemEnabled",
            "requestData": {
                "sceneName": scene_name,
                "sceneItemId": self.GetSceneItemId(scene_name, source_name),
                "sceneItemEnabled": visibility,
            },
        }
        self.call(request)

    def GetSceneItemId(self, scene_name: str, source_name: str) -> int:
        request: {str, dict} = {
            "requestType": "GetSceneItemId",
            "requestData": {"sceneName": scene_name, "sourceName": source_name},
        }
        reply = self.call(request)
        return reply["sceneItemId"]

    def GetVersion(self) -> str:
        request: {str} = {"requestType": "GetVersion", "requestData": {}}
        reply = self.call(request)

        if reply["obsVersion"]:
            return reply["obsVersion"]
        return ""

    class Listener(threading.Thread):

        def __init__(self, ws: WebSocket):
            self._request_tracker: Dict[str, threading.Event] = {}
            self._request_replies: Dict[str, dict] = {}
            self.ws = ws
            self.logger: Logger = getLogger("OBS.LISTENER")
            self.running = True
            threading.Thread.__init__(self)

        def run(self):
            self.running = True
            self._listeningLoop()

        def _listeningLoop(self):
            while self.running:
                data = self.ws.recv()
                if not data:
                    continue
                json_data: dict[str, dict] = json.loads(data)
                op: int = json_data["op"]
                requestId: str = json_data["d"].get("requestId")
                requestType: str = json_data["d"].get("requestType")
                responseData: dict[str, dict] = json_data["d"].get("responseData")
                requestStatus: dict[str, dict] = json_data["d"].get("requestStatus")
                if requestId in self._request_tracker:
                    self._request_replies[requestId] = responseData
                    self._request_tracker[requestId].set()
                    self.logger.debug(
                        f"Added request to request tracker. ID: {requestId} - Status: {requestStatus} - Type: {requestType}"
                    )
                self.logger.debug(f"Received Event: {data}")

        async def reply_handler(self, id):
            response = None
            while not response:
                response = self._request_tracker.get(id)
            #  await asyncio.sleep(0.2)
            return response
