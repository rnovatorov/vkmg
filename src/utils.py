from functools import wraps
from .exceptions import ConfigValueIsNoneException


def check_config(config):
    attr_names = [attr_name for attr_name in dir(config)
                  if not attr_name.startswith("__")]
    for attr_name in attr_names:
        if getattr(config, attr_name) is None:
            raise ConfigValueIsNoneException(attr_name)

def escape_filename(filename, rules=None):
    default_rules = {
        "/": "_",
        "\\": "_",
        "|": "_",
        "<": "_",
        ">": "_",
        ":": "_",
        ";": "_",
        "?": "_",
        "*": "_",
        "\"": "_",
        "'": "_"
    }
    if rules is not None:
        default_rules.update(rules)
    for bad_char, good_char in default_rules.items():
        filename = filename.replace(bad_char, good_char)
    return filename.strip()

def filename_escaped(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        return escape_filename(func(*args, **kwargs))
    return wrapper


def positive_int(x):
    i = int(x)
    if i > 0:
        return i
    raise TypeError("%s in not a positive int" % x)
