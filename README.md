# kucoin-websocket
Multi-threaded KuCoin WebSocket with self-management mechanisms to ensure stable streaming at all times. More control and abstraction than the native [kucoin-python-sdk](https://github.com/Kucoin/kucoin-python-sdk).
> **Note**
> This package is still under development and probably will not contain the full functionality described under [KuCoin documentation](https://docs.kucoin.com/#websocket-feed)!

## Features
### Subscription Strategy
According to [KuCoin documentations](https://docs.kucoin.com/#request-rate-limit), maximum number of batch subscriptions is **100 topics per 10 seconds**. KuCoin policy is to ignore the rest of the subscriptions if the limitation is violated. To avoid this behavior, a configurable **Backoff Strategy** is used to keep congestion low while allowing for asynchronous subscription.

### Auto-connect on Errors
There are numerous errors that can occur during the stream ([KuCoin errors](https://docs.kucoin.com/#request)) that can interrupt the stream flow. Most of the errors are *TimeOut* or *ConnectionClosed* and such errors are generally not a big concern due to network volatility, so the WebSocket tries to reconnect at most 5 times before giving up.

### Auto-Token Renewal
Currently, KuCoin tokens expire after **24 hours** ([KuCoin FAQ](https://docs.kucoin.com/#faq)) and the stream is stopped immediately. To overcome this, WebSocket details like *token* and *endpoint* are renewed after an interval, so that the connection stays alive at all time. Default interval is set to **12 hours** to leave no room for error.

### Limitless Subscriptions
KuCoin has a limitation of maximum **300 active subscriptions** at the time ([KuCoin FAQ](https://docs.kucoin.com/#faq)). To scale the subscriptions, multiple WebSockets are automatically created on parallel threads that at most **200 subscriptions**. (*to my experience, better not challenge the threshold* ^_^)

## Credits
- [python-kucoin](https://github.com/sammchardy/python-kucoin) by sammchardy

## 🤝 Contribution 
Your contributions are welcomed, as always!
