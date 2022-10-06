# Standard imports
import asyncio
from apscheduler.schedulers.background import BackgroundScheduler

# Third-party imports
from ws import ReconnectingWebsocket


class KucoinSocketManager():

    def __init__(self, markets: list, timeframe: str = "5min", refresh_hours: int = 12, backoff_factor: float = 0.1) -> None:
        """
            Initialise the IdexSocketManager

            Parameters:
                markets (list): List of markets to subscribe to
                timeframe (str): Timeframe to subscribe to
                refresh_hours (int): How often to refresh the WebSocket details
                backoff_factor (float): Backoff factor for subscribing to the WebSocket
        """

        self._conn = None
        self.markets = markets
        self._timeframe = timeframe
        self.backoff_factor = backoff_factor
        self.loop = asyncio.get_event_loop()                        # Create the main event loop
        self._conn = ReconnectingWebsocket(self.loop, self._recv)   # Create the websocket

        # Automatically refresh token to keep connection to server alive
        self.scheduler = BackgroundScheduler()
        self.scheduler.add_job(
            func = self._conn.refresh_ws_details,
            trigger = "interval",
            hours = refresh_hours,
            id = "Token Refresh Scheduler"
        )


    async def _recv(self, msg: dict) -> None:
        """ Mirror data messages to the callback """
        if 'data' in msg:
            await self.__receive(msg)


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
            sub_wait *= self.backoff_factor         # Increase wait time for each subscription
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
            sub_wait *= self.backoff_factor         # Increase wait time for each subscription
            await self.unsubscribe_kline(market)    # Unsubscribe


    async def __receive(self, msg: dict) -> None:
        """ callback function that receives messages from the socket """
        if "candles" in msg["topic"]:
            print(f"{msg['data']}")


    def run(self) -> None:
        """ Start the websocket main event loop and schedulers """        
        self.scheduler.start()                          # Start the scheduler
        self.loop.run_until_complete(self.__main())     # Start the main event loop


    async def __main(self) -> None:
        """ Main event loop """

        # Subscribe markets to Kline channels
        await self.subscribe_kline_bulk(self.markets)

        # Sleep to keep the event loop alive
        while True:
            await asyncio.sleep(20)