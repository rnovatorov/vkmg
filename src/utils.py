from functools import wraps
from .exceptions import ConfValueIsNoneException


def check_configs(conf):
    attr_names = [an for an in dir(conf) if not an.startswith("__")]
    for an in attr_names:
        if getattr(conf, an) is None:
            raise ConfValueIsNoneException(an)


def escape_filename(filename, rules=None):
    default_rules = {"/": "-"}
    if rules is not None:
        default_rules.update(rules)
    for bad_char, good_char in default_rules.items():
        filename = filename.replace(bad_char, good_char)
    return filename


def filename_escaped(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        return escape_filename(func(*args, **kwargs))
    return wrapper


def posint(x):
    i = int(x)
    if i <= 0:
        raise TypeError("%s in not a positive integer" % x)
    else:
        return i
