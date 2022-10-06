# Third-party imports
from kucoin_websocket.manager import KucoinWebSocketManager


async def receive( msg: dict) -> None:
    """ callback function that receives messages from the socket """
    if "candles" in msg["topic"]:
        print(f"{msg['data']}")



if __name__ == "__main__":

    ksm = KucoinWebSocketManager(
        callback = receive,
        markets = ["BTC-USDT", "ETH-USDT", "BNB-USDT"],
        timeframe = "1min",
        refresh_hours = 12
    )
    ksm.start()