##########################################################
#
# Copyright (C) 2021-PRESENT: Keivan Ipchi Hagh
#
# Email:    keivanipchihagh@gmail.com
# GitHub:   https://github.com/keivanipchihagh
#
##########################################################

# Third-party imports
from kucoin_websocket.manager import KucoinSocketManager


if __name__ == "__main__":

    ksm = KucoinSocketManager(
        markets = ["BTC-USDT", "ETH-USDT", "BNB-USDT"],
        timeframe = "1min",
        refresh_hours = 12
    )
    ksm.run()