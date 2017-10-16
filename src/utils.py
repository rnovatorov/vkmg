from .exceptions import ConfValueIsNoneException


def check_configs(conf):
    attr_names = [an for an in dir(conf) if not an.startswith("__")]
    for an in attr_names:
        if getattr(conf, an) is None:
            raise ConfValueIsNoneException(an)
