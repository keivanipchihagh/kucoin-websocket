# Standard imports
import asyncio

def get_or_create_eventloop() -> asyncio.AbstractEventLoop:
    """ Gets or creates an event loop. A new loop is created if ran from inside a thread """
    try:
        return asyncio.get_event_loop()
    except RuntimeError:
        asyncio.set_event_loop(asyncio.new_event_loop())
        return asyncio.get_event_loop()