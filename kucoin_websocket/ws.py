# Standard imports
import websockets as ws
from random import random
import asyncio, time, json
from typing import Callable
from datetime import datetime

# Third-party imports
from .utils.base_request import BaseRequests


class KuCoinWebSocketDetails():

    def __init__(self, base_url: str, api_version: str) -> None:
        """
            Applies for a connect token, which is used to establish a WebSocket connection (https://docs.kucoin.com/#apply-connect-token).

            Parameters:
                base_url (str): Base URL for KuCoin API
                api_version (str): API Version
        """

        self._base_url = base_url
        self._public_uri = f"/api/{api_version}/bullet-public"       # Private topics
        self._private_uri = f"/api/{api_version}/bullet-private"     # Public topics
        self._ws_details = None
        self._base_request = BaseRequests()


    @classmethod
    def create(cls, base_url: str = "https://api.kucoin.com", api_version: str = "v1") -> "KuCoinWebSocketDetails":
        self = cls(base_url = base_url, api_version = api_version)
        self._ws_details = self._base_request.post(self.url).json()["data"]
        return self


    @property
    def url(self) -> str: return f"{self._base_url}{self._public_uri}"

    @property
    def token(self) -> str: return self._ws_details["token"]

    @property
    def endpoint(self) -> str: return self._ws_details["instanceServers"][0]["endpoint"]

    @property
    def encrypt(self) -> str: return self._ws_details["instanceServers"][0]["encrypt"]

    @property
    def pingInterval(self) -> int: return self._ws_details["instanceServers"][0]["pingInterval"]

    @property
    def pingTimeout(self) -> int: return int(self._ws_details["instanceServers"][0]["pingTimeout"] / (1000 * 2)) - 1



class Websocket():

    MAX_RECONNECTS = 5  # Maximum number of retries before giving up

    def __init__(self, loop: asyncio.AbstractEventLoop, coro: Callable) -> None:
        self._loop = loop
        self._coro = coro
        self._reconnect_attempts = 0
        self._conn = None
        self._last_ping = None
        self._socket = None

        self.refresh_ws_details()   # Get a new token
        self._connect()             # Connect to the WebSocket


    def _connect(self):
        """ Runs the main event loop """
        self._conn = asyncio.ensure_future(self._run(), loop = self._loop)


    def refresh_ws_details(self) -> None:
        """ Refreshes the WebSocket details. The is essential for the WebSocket to stay connected in case the old token expires """
        print(f"[DEBUG - {self.now}] Refreshing WebSocket details")
        self._ws_details = KuCoinWebSocketDetails.create()


    async def _run(self) -> None:

        keep_waiting = True
        self._last_ping = time.time()  # record last ping

        async with ws.connect(self.ws_endpoint, ssl = self._ws_details.encrypt) as socket:
            self._socket = socket
            self._reconnect_attempts = 0

            try:
                while keep_waiting:
                    if time.time() - self._last_ping > self._ws_details.pingTimeout:
                        await self.send_ping()
                    try:
                        evt = await asyncio.wait_for(self._socket.recv(), timeout = self._ws_details.pingTimeout)
                    except asyncio.TimeoutError:
                        print(f"[DEBUG - {self.now}] No message received in {self._ws_details.pingTimeout} seconds")
                        await self.send_ping()
                    except asyncio.CancelledError:
                        print(f"[DEBUG - {self.now}] Event loop cancelled")
                        await self._socket.ping()
                    else:
                        try:
                            evt_obj = json.loads(evt)
                        except ValueError:
                            pass
                        else:
                            await self._coro(evt_obj)

            except ws.ConnectionClosed:
                # Catch connection closed and attempt to reconnect
                keep_waiting = False
                print(f"[WARNING - {self.now}] Websocket connection closed. Reconnecting...")
                await self._reconnect()

            except Exception as ex:
                # Catch all exceptions to prevent the event loop from dying, then attempt to reconnect
                keep_waiting = False
                print(f"[ERROR - {self.now}] Websocket threw an exception: {str(ex)}")
                await self._reconnect()


    async def _reconnect(self):
        """ Reconnect to the websocket """
        await self.cancel()
        self._reconnect_attempts += 1

        if self._reconnect_attempts < self.MAX_RECONNECTS:
            print(f"[WARNING - {self.now}] Websocket attemting to reconnect.. ({self._reconnect_attempts}/{self.MAX_RECONNECTS})")
            reconnect_wait = self.get_reconnect_wait(self._reconnect_attempts)
            await asyncio.sleep(reconnect_wait)
            self._connect()
        else:
            print(f"[ERROR - {self.now}] Websocket could not reconnect after {self._reconnect_attempts} attempts")


    async def send_ping(self):
        """ Sends a keepalive ping to the server """
        await self._socket.send(json.dumps({
            'id': self.random_id,
            'type': 'ping'
        }))
        self._last_ping = time.time()


    async def send_message(self, msg: dict, retry_count: int = 0):
        """ Sends a message to the server """
        if not self._socket:
            if retry_count < 5:
                await asyncio.sleep(1)
                await self.send_message(msg, retry_count + 1)
        else:
            await self._socket.send(json.dumps({
                "id": self.random_id,
                **msg
            }))


    async def cancel(self):
        """ Cancel main event loop """
        try:
            self._conn.cancel()
        except asyncio.CancelledError:
            pass


    def get_reconnect_wait(self, attempts: int):
        """ Exponential backoff """
        return round(random() * min(self.MAX_RECONNECTS, 2 ** attempts - 1) + 1)


    @property
    def random_id(self):
        """ Random ID based on current time """
        return str(int(time.time() * 1000))    

    @property
    def ws_endpoint(self) -> str:
        """ Full Websocket endpoint for receiving data """
        return f"{self._ws_details.endpoint}?token={self._ws_details.token}&connectId={self.random_id}"
    
    @property
    def now(self) -> datetime:
        """ Current date time """
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S')