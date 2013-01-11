import sys

class NothingReporter(object):

    def report(self, *args, **kwargs):
        pass

    def inline(self, *args, **kwargs):
        pass

    def error(self, *args, **kwargs):
        pass


class StatusReporter(object):

    def __init__(self, *args, **kwargs):
        self.level_symbol = '  '
        self.started = False

    def report(self, message, level=0, stream=sys.stdout):
        if self.started:
            print >>stream, ''
        else:
            self.started = True

        if level:
            message = (self.level_symbol * level) + message

        print >>stream, message,
        stream.flush()

    def inline(self, message, stream=sys.stdout):
        print message,
        stream.flush()

    def error(self, message, inline=False):
        message = 'ERROR: ' + message
        if inline:
            self.inline(message, stream=sys.stderr)
        else:
            self.report(message, stream=sys.stderr)
