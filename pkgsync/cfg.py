import os
import requests
from .util import FileLikeResponseAdapter

class ConfigFetcher(object):

    def __init__(self, uri, *args, **kwargs):
        self.uri = uri

    def fetch(self):
        raise NotImplementedError()

class LocalConfigFetcher(ConfigFetcher):

    def fetch(self):
        if self.uri.startswith('file://'):
            self.uri = self.uri[7:]

        if os.path.exists(self.uri):
            try:
                return open(self.uri, 'r')
            except OSError, IOError:
                pass

class HttpConfigFetcher(ConfigFetcher):

    def __init__(self, uri, username=None, password=None, **kwargs):
        self.uri = uri
        self.username = username
        self.password = password
        self.request_kwargs = kwargs

    def fetch(self):
        if self.uri.startswith('http://') or self.uri.startswith('https://'):
            return self._get()

    def _get(self):
        if self.username and self.password:
            self.request_kwargs.setdefault('auth', (self.username, self.password))
        self.request_kwargs.setdefault('stream', True)
        response = requests.get(self.uri, **self.request_kwargs)
        if response.status_code == 401:
            raise RuntimeError('Incorrect username/password for %s' % self.uri)
        response.raise_for_status()
        return FileLikeResponseAdapter(response)
