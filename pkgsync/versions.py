import pkg_resources
from ConfigParser import RawConfigParser, NoOptionError, NoSectionError
from UserDict import IterableUserDict

from .cfg import LocalConfigFetcher, HttpConfigFetcher
from .util import name_version

class Versions(set):
    """ A set of release specifications that can be instantiated from a uri to
    a buildout-style `ConfigParser` cfg file, from a `Repository`, or by the
    can just be instantiated with a list of release specifications, such as::

        Versions(['Django>1.4.1,<1.5', 'django-logtail', 'South>=0.7.5'])
    """

    config_fetchers = [
        LocalConfigFetcher,
        HttpConfigFetcher,
    ]

    @classmethod
    def from_uri(cls, uri, **kwargs):
        """
        :param uri: The URI of a cfg file containing package names and versions
            in the following form (the cfg file can also contain other stanzas)::

                [versions]
                iw.fss = 2.7.1
                zkaffold = 0.0.8
                zc.buildout = 1.4.3
        """
        for fetcher in cls.config_fetchers:
            fp = fetcher(uri, **kwargs).fetch()
            if fp:
                return cls.from_cfg_fp(fp)

        raise RuntimeError('Unrecognised versions.cfg URI %s' % uri)

    @classmethod
    def from_cfg_fp(cls, fp):
        """
        Generate a versions specification from a file-like object containing
        buildout cfg-style versions tuples

        :param fp: A file-like object (specifically requires ``.readline()``)
        :returns: An instantiated `Versions` object.
        """
        config = RawConfigParser()
        config.optionxform = str # incantation to make keys case-sensitive
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

        return cls(versions)

    @classmethod
    def all_packages(cls, repository):
        versions = repository.packages()
        return cls(versions)

    def specs_for(self, package_name):
        """Yield the specs which refer to the given package name"""
        for spec in self:
            spec_as_req = pkg_resources.Requirement.parse(spec)
            if spec_as_req.project_name == package_name:
                yield spec
