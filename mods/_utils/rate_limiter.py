import functools
import threading


def RateLimiter(limit, cooldown=60):
    def decorator(func):
        semaphore = threading.Semaphore(limit)
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            semaphore.acquire(timeout=cooldown)
            try:
                return func(*args, **kwargs)
            finally:
                timer = threading.Timer(cooldown, semaphore.release,daemon=True)
                timer.start()

        return wrapper

    return decorator