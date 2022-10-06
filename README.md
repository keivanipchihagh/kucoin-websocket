# kucoin-websocket
Multi-threaded KuCoin WebSocket with self-management mechanisms to ensure stable streaming at all times.

## Features
### Subscription Strategy
According to [KuCoin documentations](https://docs.kucoin.com/#request-rate-limit), maximum number of batch subscriptions at a time is **100 topics per 10 seconds**. KuCoin policy is to ignore the rest of the subscriptions if the limitation is violated. To avoid this behavior, a configurable **Backoff Strategy** is used to keep congestion low.

### Auto-Reconnect on Errors
There are numerous errors that can occure during the stream ([KuCoin errors](https://docs.kucoin.com/#request)) that can interrupt the stream flow. Most of the errors are *TimeOut* or *ConnectionClosed* and such that are not a great concern, so the websocket tries to reconnect at most 5 times before giving up.

### Token Renewal
Currently, KuCoin tokens expire after **24 hours** ([KuCoin FAQ](https://docs.kucoin.com/#faq)) and the stream is stopped. To overcome this, WebSocket details like *token* and *endpoint* are renewed after an interval, so that the connection stays alive at all time. Default interval is set to **12 hours** to leave no room for error.

### Active Subscriptions
KuCoin has a limitation of the number of active subscriptions which is 300 at the time ([KuCoin FAQ](https://docs.kucoin.com/#faq)). To solve the issue, multiple WebSockets are automatically created on different threads that run in parallel and hold at most 250 subscriptions (*let's not mess with the limitation!*).
