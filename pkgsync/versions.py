import os
import requests
from ConfigParser import RawConfigParser, NoOptionError, NoSectionError

from .util import FileLikeResponseAdapter


class ConfigFetcher(object):

    def __init__(self, uri, *args, **kwargs):
        self.uri = uri

    def fetch(self):
        raise NotImplementedError()

class LocalConfigFetcher(ConfigFetcher):

    def fetch(self):
        if self.uri.startswith('file://'):
            self.uri = self.uri[:7]

        if os.path.exists(self.uri):
            try:
                return open(self.uri, 'r')
            except OSError, IOError:
                pass


class HttpConfigFetcher(ConfigFetcher):

    def __init__(self, uri, username=None, password=None):
        self.uri = uri
        self.username = username
        self.password = password

    def fetch(self):
        if self.uri.startswith('http://') or self.uri.startswith('https://'):
            return self._get()

    def _get(self, **kwargs):
        if self.username and self.password:
            kwargs.setdefault('auth', (self.username, self.password))
        kwargs.setdefault('stream', True)
        response = requests.get(self.uri, **kwargs)
        if response.status_code == 401:
            raise RuntimeError('Incorrect username/password for %s' % self.uri)
        response.raise_for_status()
        return FileLikeResponseAdapter(response)


class Versions(object):

    fetchers = [
        LocalConfigFetcher,
        HttpConfigFetcher,
    ]

    def __init__(self, f):
        '''f should be file-like with a readline method'''
        self.f = f

    @classmethod
    def from_uri(cls, uri, **kwargs):
        for fetcher in cls.fetchers:
            raw = fetcher(uri, **kwargs).fetch()
            if raw:
                return cls(raw)

        raise RuntimeError('Unrecognised versions.cfg URI %s' % uri)

    def versions(self):
        config = RawConfigParser()
        config.readfp(self.f)

        try:
            versions_name = config.get('buildout', 'versions')
        except NoSectionError, NoOptionError:
            versions_name = 'versions'

        if not config.has_section(versions_name):
            raise RuntimeError('No versions section')

        versions_dict = {}

        for package_name in config.options(versions_name):
            versions_dict[package_name] = config.get(versions_name, package_name)

        return versions_dict
