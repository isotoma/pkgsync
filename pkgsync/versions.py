import os
import requests
from UserDict import IterableUserDict
from ConfigParser import RawConfigParser, NoOptionError, NoSectionError

from .util import FileLikeResponseAdapter, name_version


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


class Versions(IterableUserDict):

    config_fetchers = [
        LocalConfigFetcher,
        HttpConfigFetcher,
    ]

    def __init__(self, versions={}, **kwargs):
        IterableUserDict.__init__(self, dict=versions, **kwargs)

    @classmethod
    def from_uri(cls, uri, **kwargs):
        """
        The URI of a cfg file containing package names and versions in the
        following form::

            [versions]
            iw.fss = 2.7.1
            zkaffold = 0.0.8
            zc.buildout = 1.4.3
        """
        for fetcher in cls.config_fetchers:
            fp = fetcher(uri, **kwargs).fetch()
            if fp:
                return cls.from_fp(fp)

        raise RuntimeError('Unrecognised versions.cfg URI %s' % uri)

    @classmethod
    def from_names(cls, names_list):
        """
        Take a list of package names, optionally with version numbers, e.g.

            >> dictify_package_list(['foo', 'bar==1.2.3', 'bar==1.2.4', 'quux'])
            {'foo': [], 'bar': ['1.2.3', '1.2.4'], 'quux': []}
        """
        package_versions = {}

        for dist_spec in names_list:
            name, version = name_version(dist_spec)
            if not name in package_versions:
                package_versions[name] = []
            if version and not version in package_versions[name]:
                package_versions[name].append(version)

        return cls(package_versions)

    @classmethod
    def from_fp(cls, fp):
        config = RawConfigParser()
        config.readfp(fp)

        try:
            versions_name = config.get('buildout', 'versions')
        except NoSectionError, NoOptionError:
            versions_name = 'versions'

        if not config.has_section(versions_name):
            raise RuntimeError('No versions section')

        versions_dict = {}

        for package_name in config.options(versions_name):
            versions_dict[package_name] = config.get(versions_name, package_name)

        return cls(versions_dict)
