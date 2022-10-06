# Standard imports
import asyncio
from typing import Callable
from apscheduler.schedulers.background import BackgroundScheduler

# Third-party imports
from .threads import ThreadPool
from .ws import ReconnectingWebsocket
from .utils import get_or_create_eventloop


class KucoinWebSocket():

    def __init__(self, callback: Callable, markets: list, timeframe: str = "5min", refresh_hours: int = 12, backoff_factor: float = 0.1) -> None:
        """
            Initialise the KucoinWebSocket

            Parameters:
                callback (Callable): callback function that receives messages from the socket
                markets (list): List of markets to subscribe to
                timeframe (str): Timeframe to subscribe to
                refresh_hours (int): How often to refresh the WebSocket details
                backoff_factor (float): Backoff factor for subscribing to the WebSocket
        """

        self._conn = None
        self._markets = markets
        self._callback = callback
        self._timeframe = timeframe
        self._refresh_hours = refresh_hours
        self._backoff_factor = backoff_factor
        self._scheduler = BackgroundScheduler()


    async def _recv(self, msg: dict) -> None:
        """ Mirror data messages to the callback """
        if 'data' in msg:
            await self._callback(msg)


    async def subscribe_kline(self, market: str) -> None:
        """ Subscribe to a channel """
        await self._conn.send_message({
            'type': 'subscribe',
            'topic': f"/market/candles:{market}_{self._timeframe}",
            'response': True
        })


    async def subscribe_kline_bulk(self, markets: list) -> None:
        """ Subscribe to a list of market channels with backoff_factor to keep congestion to a minimum """
        sub_wait = 0.5                              # Start with 0.5 second wait
        for market in markets:            
            await asyncio.sleep(sub_wait)           # Sleep
            sub_wait *= self._backoff_factor        # Increase wait time for each subscription
            await self.subscribe_kline(market)      # Subscribe


    async def unsubscribe_kline(self, topic: str) -> None:
        """ Unsubscribe from a channel """
        await self._conn.send_message({
            'type': 'unsubscribe',
            'topic': topic,
            'response': True
        })


    async def unsubscribe_kline_bulk(self, markets: list) -> None:
        """ Unsubscribe to a list of market channels with backoff_factor to keep congestion to a minimum """
        sub_wait = 0.5                              # Start with 0.5 second wait
        for market in markets:
            await asyncio.sleep(sub_wait)           # Sleep
            sub_wait *= self._backoff_factor        # Increase wait time for each subscription
            await self.unsubscribe_kline(market)    # Unsubscribe


    def run(self) -> None:
        """ Start the websocket main event loop and schedulers """

        self._loop = get_or_create_eventloop()                      # Create the main event loop
        self._conn = ReconnectingWebsocket(self._loop, self._recv)  # Create the websocket

        # Automatically refresh token to keep connection to server alive
        self._scheduler.add_job(
            func = self._conn.refresh_ws_details,
            trigger = "interval",
            hours = self._refresh_hours,
        )
        self._scheduler.start()                         # Start the scheduler
        self._loop.run_until_complete(self.__main())    # Start the main event loop



    async def __main(self) -> None:
        """ Main event loop """

        # Subscribe markets to Kline channels
        await self.subscribe_kline_bulk(self._markets)

        # Sleep to keep the event loop alive
        while True:
            await asyncio.sleep(30)



class KucoinWebSocketManager():

    MAX_SUBSCRIPTIONS = 200     # KuCoin supports up to 300 subscriptions per connection

    def __init__(self, callback: Callable, markets: list, timeframe: str = "5min", refresh_hours: int = 12, backoff_factor: float = 0.1) -> None:
        """
            Initialise the IdexSocketManager

            Parameters:
                callback (Callable): callback function that receives messages from the socket
                markets (list): List of markets to subscribe to
                timeframe (str): Timeframe to subscribe to
                refresh_hours (int): How often to refresh the WebSocket details
                backoff_factor (float): Backoff factor for subscribing to the WebSocket
        """

        self.thread_pool = ThreadPool(
            confs = {f"worker {i // self.MAX_SUBSCRIPTIONS}": (KucoinWebSocket(callback, markets[i: i + self.MAX_SUBSCRIPTIONS], timeframe, refresh_hours, backoff_factor).run, ()) for i in range(0, len(markets), self.MAX_SUBSCRIPTIONS)}
        )


    def start(self) -> None:
        """ Runs the thread pool """
        self.thread_pool.start()