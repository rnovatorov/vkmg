class LoginFailedException(Exception):

    def __str__(self):
        return "Login failed"


class CannotProceedToAudiosException(Exception):

    def __init__(self, expected, got):
        self.expected = expected
        self.got = got

    def __str__(self):
        return ("Cannot proceed to audios: instead of %s got %s"
                % (self.expected, self.got))


class ConfValueIsNoneException(Exception):

    def __init__(self, attr_name):
        self.attr_name = attr_name

    def __str__(self):
        return "conf.%s is not set" % self.attr_name
