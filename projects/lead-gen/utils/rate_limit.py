"""Rate limiting and retry utilities."""

import time
import functools
import random


def retry(max_attempts: int = 3, base_delay: float = 2.0, exceptions=(Exception,)):
    """Decorator: retry on specified exceptions with exponential backoff + jitter."""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except exceptions as exc:
                    if attempt == max_attempts - 1:
                        raise
                    delay = base_delay * (2 ** attempt) + random.uniform(0, 1)
                    print(f"  Retry {attempt + 1}/{max_attempts - 1} after error: {exc}. Waiting {delay:.1f}s...", flush=True)
                    time.sleep(delay)
        return wrapper
    return decorator


def rate_limited(calls_per_second: float = 1.0):
    """Decorator: enforce a minimum delay between calls."""
    min_interval = 1.0 / calls_per_second
    last_called = [0.0]

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            elapsed = time.time() - last_called[0]
            wait = min_interval - elapsed
            if wait > 0:
                time.sleep(wait)
            result = func(*args, **kwargs)
            last_called[0] = time.time()
            return result
        return wrapper
    return decorator


def sleep_between(min_s: float = 0.5, max_s: float = 2.0):
    """Sleep a random amount between min_s and max_s seconds."""
    time.sleep(random.uniform(min_s, max_s))
