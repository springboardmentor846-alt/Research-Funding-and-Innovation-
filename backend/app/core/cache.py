import time
from functools import wraps


def ttl_cache(seconds: int = 300):
    """
    Simple in-memory cache decorator with time-based expiry.
    Caches results per unique set of arguments for `seconds` seconds.
    Used to avoid repeatedly hitting slow/rate-limited external APIs
    (Grants.gov, PatentsView, OpenAlex) for the same query.
    """
    def decorator(func):
        cache_store = {}

        @wraps(func)
        def wrapper(*args, **kwargs):
            key = (args, tuple(sorted(kwargs.items())))
            now = time.time()

            if key in cache_store:
                cached_result, cached_at = cache_store[key]
                if now - cached_at < seconds:
                    return cached_result

            result = func(*args, **kwargs)
            cache_store[key] = (result, now)
            return result

        return wrapper
    return decorator