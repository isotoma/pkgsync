import re
import pkginfo

from .exceptions import InvalidDistribution

class Metadata(object):
    """An adapter around pkginfo with better support for classifiers and
    keywords. Also crucially adds upload and register methods for creating a
    distutils-compatible representation of the package suitable for upload to a
    python distribution repository"""

    def __init__(self, dist):
        self.dist = dist
        self._meta = self._introspect()

    def __getattr__(self, name):
        if hasattr(self._meta, name):
            return getattr(self._meta, name)
        return object.__getattribute__(self, name)

    def _parse_classifiers(self, metadata_dump):
        return re.findall('\nClassifier: (.* :: .*)', metadata_dump)

    def _introspect(self):
        """ Get the pkginfo metadata and monkeypatch where required """
        metadata = pkginfo.get_metadata(self.dist.path)
        if not metadata:
            raise InvalidDistribution(self.dist.path)

        metadata_full = metadata.read()
        if metadata.classifiers == () and 'Classifier' in metadata_full:
            metadata.classifiers = self._parse_classifiers(metadata_full)

        if metadata.keywords and not isinstance(metadata.keywords, (tuple, list)):
            keywords = metadata.keywords.split(',')
            if len(keywords) == 1:
                keywords = metadata.keywords.split(' ')
            metadata.keywords = keywords
        return metadata

    def upload(self):
        """ Build a dictionary suitable for a distutils upload request """
        return {
            ':action': 'file_upload',
            'protocol_version': '1',
            'name': self._meta.name,
            'version': self._meta.version,
            'filetype': self._meta.__class__.__name__.lower(),
            'pyversion': '',
            'md5_digest': self.dist.md5_digest,
            'content': (self.dist.basename, self.dist.content),
        }

    def register(self):
        return {
            ':action': 'submit',
            'metadata_version' : self._meta.metadata_version,
            'name': self._meta.name or 'UNKNOWN',
            'version': self._meta.version or '0.0.0',
            'summary': self._meta.summary or 'UNKNOWN',
            'home_page': self._meta.home_page or 'UNKNOWN',
            'author': self._meta.author or 'UNKNOWN',
            'author_email': self._meta.author_email or 'UNKNOWN',
            'license': self._meta.license or 'UNKNOWN',
            'description': self._meta.description or 'UNKNOWN',
            'keywords': self._meta.keywords or [],
            'platform': self._meta.platforms,
            'classifiers': self._meta.classifiers,
            'download_url': self._meta.download_url or 'UNKNOWN',
            'provides': self._meta.provides,
            'requires': self._meta.requires,
            'obsoletes': self._meta.obsoletes,
        }

class OldStyleMetadata(object):
    """ A pretend metadata parser for old distributions that you want to upload
    to your distribution repository, but that lack the crucial setuptools
    PKG-INFO metadata.

    This very simply splits the filename into a package name and version, which
    are then provided via the upload and register dictionaries along with every
    other metadata attribute filled in with 'UNKNOWN' data."""

    parser = re.compile('^([A-Za-z]+)-(.*)\.(tgz|tar\.gz)$')

    def __init__(self, dist):
        self.dist = dist
        self.name, self.version = self._parse_basename()

    def _parse_basename(self):
        try:
            return self.parser.match(self.dist.basename).groups()[:2]
        except (IndexError, AttributeError):
            raise InvalidDistribution(self.dist.path)

    def upload(self):
        return {
            ':action': 'file_upload',
            'protocol_version': '1',
            'name': self.name,
            'version': self.version,
            'filetype': 'sdist',
            'pyversion': '',
            'md5_digest': self.dist.md5_digest,
            'content': (self.dist.basename, self.dist.content),
        }

    def register(self):
        """ Build a dictionary suitable for a distutils register request """
        return {
            ':action': 'submit',
            'metadata_version' : '1.0', # lies
            'name': self.name,
            'version': self.version,
            'summary': 'UNKNOWN',
            'home_page': 'UNKNOWN',
            'author': 'UNKNOWN',
            'author_email': 'UNKNOWN',
            'license': 'UNKNOWN',
            'description': 'UNKNOWN',
            'keywords': [],
            'platform': ['UNKNOWN'],
            'classifiers': (),
            'download_url': 'UNKNOWN',
            'provides': (),
            'requires': (),
            'obsoletes': (),
        }
