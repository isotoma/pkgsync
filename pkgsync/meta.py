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
        metadata = self._introspect()

        return {
            ':action': 'file_upload',
            'protocol_version': '1',
            'name': metadata.name,
            'version': metadata.version,
            'filetype': metadata.__class__.__name__.lower(),
            'pyversion': '',
            'md5_digest': self.dist.md5_digest,
            'content': (self.dist.basename, self.dist.content),
        }

    def register(self):
        """ Build a dictionary suitable for a distutils register request """
        meta = self._introspect()

        return {
            ':action': 'submit',
            'metadata_version' : meta.metadata_version,
            'name': meta.name or 'UNKNOWN',
            'version': meta.version or '0.0.0',
            'summary': meta.summary or 'UNKNOWN',
            'home_page': meta.home_page or 'UNKNOWN',
            'author': meta.author or 'UNKNOWN',
            'author_email': meta.author_email or 'UNKNOWN',
            'license': meta.license or 'UNKNOWN',
            'description': meta.description or 'UNKNOWN',
            'keywords': meta.keywords or [],
            'platform': meta.platforms,
            'classifiers': meta.classifiers,
            'download_url': meta.download_url or 'UNKNOWN',
            'provides': meta.provides,
            'requires': meta.requires,
            'obsoletes': meta.obsoletes,
        }
