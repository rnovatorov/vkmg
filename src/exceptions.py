class LoginFailedException(Exception):
    pass


class CannotProceedToAudiosException(Exception):
    pass


class ConfValueIsNoneException(Exception):

    def __init__(self, attr_name):
        self.attr_name = attr_name

    def __str__(self):
        return "conf.%s is not set" % self.attr_name
