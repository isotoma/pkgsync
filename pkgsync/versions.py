from UserDict import IterableUserDict
from ConfigParser import RawConfigParser, NoOptionError, NoSectionError

from .cfg import LocalConfigFetcher, HttpConfigFetcher
from .util import name_version

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
