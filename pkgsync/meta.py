import re
import pkginfo

from .exceptions import InvalidDistribution

class Metadata(object):

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
        """ Build a dictionary suitable for a distutils register request """
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
