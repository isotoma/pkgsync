import re
import os
import urllib
import urlparse
from .exceptions import InvalidRemoteDistribution
from .dist import Distribution
from .digest import IteratingMd5Checker

class RemoteDistribution(object):
    """A distribution on a remote repository"""

    def __init__(self, repository, path, package_name):
        """
        :param repository: A `Repository` object
        :param path: The path to the distribution on the repository, relative
            to `Repository.package_index` for this package_name
        :param package_name: The name of the package that this distribution is
            for
        """
        self.repository = repository
        self.path = path
        self.package_name = package_name
        self.parse_path()

    def _parse_distribution_name(self):
        if self.basename.endswith('.egg'):
            parser = re.compile(r'^(?P<package_name>%s)-' \
                '(?P<version>.*)(-)' \
                '(?P<pyversion>py[\d\.]+)' \
                '(?P<extension>\.egg)$' % (self.package_name,)
            )
        else:
            parser = re.compile(r'^(?P<package_name>%s)-' \
                '(?P<version>.*)' \
                '(?P<extension>\.zip|\.tgz|\.tar\.gz|\.tar\.bz2)$' % (
                self.package_name,)
            )
        r = parser.search(self.basename)
        if r:
            return r.groupdict()

    def _parse_digest(self):
        return urllib.splitvalue(urlparse.urldefrag(self.path)[1])[1]

    def _parse_basename(self):
        defragged = urlparse.urldefrag(self.path)[0]
        return urllib.unquote(defragged.split('/')[-1])

    def _save_data(self, what, where, md5_check=None):
        f = open(where, 'wb')
        f.write(what)
        f.close()

        if md5_check:
            IteratingMd5Checker(where, md5_check).check()

        return where

    def parse_path(self):
        self.basename = self._parse_basename()
        parsed_name = self._parse_distribution_name()
        if not parsed_name:
            raise InvalidRemoteDistribution(self.path)
        self.version = parsed_name.get('version')
        self.pyversion = parsed_name.get('pyversion')
        self.extension = parsed_name.get('extension')
        self.md5_digest = self._parse_digest()

    @property
    def url(self):
        return urlparse.urljoin(
            self.repository.package_index(self.package_name),
            self.path,
        )

    def download(self, save_to='/tmp'):
        response = self.repository.get(self.url)
        file_path = os.path.join(save_to, self.basename)
        return Distribution(
            self._save_data(response.content, file_path, md5_check=self.md5_digest)
        )

    def __repr__(self):
        attrs = ['repository', 'path', 'md5_digest', 'version', 'basename']
        if self.pyversion:
            attrs.append('pyversion')
        r = 'RemoteDistribution('
        for attr in attrs:
            r += '%s=%r, ' % (attr, getattr(self, attr))
        return r.rstrip(', ') + ')'

    @staticmethod
    def diff(a, b):
        """
        :param a: a list or tuple of RemoteDistribution objects
        :param b: another list/tuple of RemoteDistribution objects
        :return: a list of RemoteDistribution objects required to make b match a
        """
        b_basenames = [d.basename for d in b]
        return [d for d in a if not d.basename in b_basenames]
