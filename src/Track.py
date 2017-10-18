import os


class Track(object):
    """
    Represent a music track
    """
    def __init__(self, performer, title, tracks_dir, url=None):
        self.performer = performer
        self.title = title
        self.tracks_dir = tracks_dir
        self.url = url

    def __repr__(self):
        return "<Track(name='%s')>" % self.name

    @property
    def name(self):
        return "%s - %s" % (self.performer, self.title)

    @property
    def path(self):
        return os.path.join(self.tracks_dir, self.performer,
                            "%s.mp3" % self.title)

    @property
    def is_already_downloaded(self):
        return os.path.exists(self.path)
