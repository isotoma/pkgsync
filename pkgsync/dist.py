import os
from hashlib import md5

from .meta import Metadata, OldStyleMetadata
from .exceptions import InvalidDistribution

class Distribution(object):

    def __init__(self, path):
        self.path = path
        try:
            self.meta = Metadata(self)
        except InvalidDistribution:
            self.meta = OldStyleMetadata(self)

        self._content = None
        self._md5_digest = None

    def _load(self):
        f = open(self.path, 'rb')
        self._content = f.read()
        f.close()

    def _calculate_digest(self):
        """ Don't iterate over chunks because it's already in mem to upload """
        self._md5_digest = md5(self.content).hexdigest()

    @property
    def content(self):
        if not self._content:
            self._load()
        return self._content

    @property
    def basename(self):
        return os.path.basename(self.path)

    @property
    def md5_digest(self):
        if not self._md5_digest:
            self._calculate_digest()
        return self._md5_digest
