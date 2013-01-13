import hashlib

class Md5MismatchException(Exception):
    """
    The given md5sum does not match the md5sum of the file at the given path
    """

class IteratingMd5Checker(object):

    def __init__(self, path, against):
        self.path = path
        self.against = against

    def check(self):
        digest = self._digest()
        if not digest == self.against:
            raise Md5MismatchException(self.path, self.against)

    def _digest(self):
        md5 = hashlib.md5()
        with open(self.path,'rb') as f:
            for chunk in iter(lambda: f.read(128*md5.block_size), b''):
                md5.update(chunk)
        return md5.hexdigest()
