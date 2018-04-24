import os


class FakeConfig(object):

    def get(self, key, default=None):
        return os.environ.get(key, default)


class Application(object):

    def __init__(self, config=None):
        super(Application, self).__init__()
        self.config = config