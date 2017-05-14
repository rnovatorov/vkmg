import os
from functools import wraps


def pause_on_complete(enable=lambda: True):
    def outer(func):
        @wraps(func)
        def inner(*args, **kwargs):
            result = func(*args, **kwargs)
            if enable():
                prompt = "Function '%s' completed. Hit Enter to continue > " % func.__name__
                input(prompt)
            return result
        return inner
    return outer


def valid_directory(path):
    if os.path.isdir(path):
        return path
    else:
        raise IOError
