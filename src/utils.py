import os
from functools import wraps
from .exceptions import ConfValueIsNoneException


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


def check_configs(conf):
    attr_names = [an for an in dir(conf) if not an.startswith("__")]
    for an in attr_names:
        if getattr(conf, an) is None:
            raise ConfValueIsNoneException(an)
    return bool(conf)
