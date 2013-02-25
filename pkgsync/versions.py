import pkg_resources
from ConfigParser import RawConfigParser, NoOptionError, NoSectionError
from UserDict import IterableUserDict

from .cfg import LocalConfigFetcher, HttpConfigFetcher
from .util import name_version

class Versions(IterableUserDict):

    config_fetchers = [
        LocalConfigFetcher,
        HttpConfigFetcher,
    ]

    def __init__(self, versions, repository, latest=False, **kwargs):
        """
        :params versions:
            an iterable of package specification strings in the same form used
            in a setup.py, e.g.::

                ['Django==1.4.3', 'Django==1.4.4', 'zc.buildout>=1.4.3,<2.0']

        :params repository: A Repository object
        :params latest:
            For each package specification, select only the highest version
            package available from the packages that match the specification.
        """
        self.repository = repository
        self.versions = versions
        self._latest = latest
        self.data = {}
        self._data_latest = latest
        IterableUserDict.__init__(self, **kwargs)

    @property
    def latest(self):
        return self._latest

    @latest.setter
    def latest(self, value):
        # invalidate cache
        self._latest = value
        self.data = {}

    @classmethod
    def from_uri(cls, uri, repository, **kwargs):
        """
        :params uri: 
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
                return cls.from_cfg_fp(fp, repository)

        raise RuntimeError('Unrecognised versions.cfg URI %s' % uri)

    @classmethod
    def from_cfg_fp(cls, fp, repository):
        """
        Generate a versions specification from a file-like object containing
        buildout cfg-style versions tuples

        :params fp: A file-like object (specifically requires ``readline``)
        """
        config = RawConfigParser()
        config.readfp(fp)

        try:
            versions_name = config.get('buildout', 'versions')
        except NoSectionError, NoOptionError:
            versions_name = 'versions'

        if not config.has_section(versions_name):
            raise RuntimeError('No versions section')

        versions = []

        for package_name in config.options(versions_name):
            version = config.get(versions_name, package_name)
            versions.append('%s==%s' % (package_name, version))

        return cls(versions, repository)

    @classmethod
    def all_packages(cls, repository):
        versions = repository.package_names()
        return cls(versions, repository)

    def _package_name(self, version_spec):
        requirement = pkg_resources.Requirement.parse(version_spec)
        return requirement.project_name

    def _links_for_spec(self, spec):
        links = self.repository.download_links(self._package_name(spec))
        requirement = pkg_resources.Requirement.parse(spec)

        for link in links:
            parsed = pkg_resources.parse_version(link.version)
            if parsed in requirement:
                yield link

    def _latest_link(self, links):
        """
        Returns the latest link but in generator form, to defer the http
        requests until they need to be run, and so we can chain this method
        with the links_for_spec method
        """
        yield max(links, key=lambda i: pkg_resources.parse_version(i.version))

    def distribution_links(self):
        """
        For each package specification in self.versions, calculate a list of
        matching links to distributions on the repository. Takes into account
        self.latest.

        :rtype: 
            A dictionary of the form {'package_name': download_links_generator}
        """
        returns = {}

        for spec in self.versions:
            links = self._links_for_spec(spec)
            name = self._package_name(spec)
            if self.latest:
                returns[name] = self._latest_link(links)
            else:
                returns[name] = links

        return returns

    def __getitem__(self, key):
        if not self.data:
            self.data = self.distribution_links()
        return IterableUserDict.__getitem__(self, key)

    def __contains__(self, item):
        if not self.data:
            self.data = self.distribution_links()
        return IterableUserDict.__contains__(self, item)

    def keys(self):
        if not self.data:
            self.data = self.distribution_links()
        return IterableUserDict.keys(self)

    def __setitem__(self, key, value):
        raise NotImplementedError()
