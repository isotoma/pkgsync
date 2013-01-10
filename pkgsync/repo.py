import os
import sys
import re
import hashlib
import urllib2
import urlparse
from xml.dom.minidom import parseString
from collections import namedtuple

import requests

DistributionLink = namedtuple('DistributionLink', ['url', 'md5_digest', 'version', 'basename'])

class IteratingMd5Checker(object):

    def __init__(self, path, against):
        self.path = path
        self.against = against

    def check(self):
        digest = self._digest()
        if not digest == self.against:
            print >>sys.stderr, 'DIGEST: %s\nSHOULD: %s' % (digest, self.against)
        return digest == self.against

    def _digest(self):
        md5 = hashlib.md5()
        with open(self.path,'rb') as f: 
            for chunk in iter(lambda: f.read(128*md5.block_size), b''): 
                md5.update(chunk)
        return md5.hexdigest()


class Repository(object):

    def __init__(self, uri, username=None, password=None, simple_prefix='simple'):
        self.username = username
        self.password = password

        self.authentication = username and password

        self.uri = uri
        self.simple_prefix = 'simple'

        self._package_names = []

    def get(self, url, **kwargs):
        if self.authentication:
            kwargs.setdefault('auth', self._auth)
        response = requests.get(url, **kwargs)
        return response

    @property
    def _auth(self):
        return (self.username, self.password)

    def _simple_url(self):
        return '%s/%s' % (
            self.uri.rstrip('/'),
            self.simple_prefix,
        )

    def _package_index(self, package_name):
        return '%s/%s/' % (
            self._simple_url(),
            package_name,
        )

    def _parse_basename(self, basename):
        parser = re.compile(r'^(?P<package_name>.*)-(?P<version>.*)(?P<extension>\.zip|\.tgz|\.tar\.gz)$')
        r = parser.search(basename)
        if r:
            return r.groupdict()

    def _md5_anchor(self, link):
        r = re.compile(r'\#md5=(?P<md5_digest>[a-z0-9]{32})')
        digest = r.search(link)
        if digest:
            return digest.groups()[0]

    def _save_data(self, what, where, md5_check=None):
        f = open(where, 'wb')
        f.write(what)
        f.close()

        if md5_check:
            assert IteratingMd5Checker(where, md5_check).check()

        return where

    def download_links(self, package_name):
        request = self.get(self._package_index(package_name))
        if request.status_code == 404:
            raise StopIteration()
        if request.status_code == 401:
            raise RuntimeError('Incorrect username/password for %s' % request.request.url)
        dom = parseString(request.content)
        for link in dom.getElementsByTagName('a'):
            basename = link.firstChild.data
            parsed = self._parse_basename(basename)
            if parsed and parsed['package_name'] == package_name:
                yield DistributionLink(
                    url=urlparse.urljoin(self._package_index(package_name),
                        link.attributes['href'].value),
                    md5_digest=self._md5_anchor(link.attributes['href'].value),
                    version=parsed['version'],
                    basename=basename,
                )

    def package_names(self):
        """ Return a list of every package available in this repo """
        if not self._package_names:
            request = self.get(self._simple_url())
            dom = parseString(request.content)
            self._package_names = [e.firstChild.data for e in dom.getElementsByTagName('a')]
        return self._package_names

    def fetch_version(self, package_name, version, save_to=None):
        """ Download only the specified version of a package """
        matching_versions = [l for l in self.download_links(package_name) if l.version==version]
        try:
            link = matching_versions[0]
        except IndexError:
            return
        return self.fetch(link, save_to=save_to)

    def fetch_all(self, package_name, save_to=None):
        """ Download all versions of the named package """
        for link in self.download_links(package_name):
            yield fetch(link, save_to=save_to)

    def fetch(self, distribution_link, save_to=None):
        request = self.get(distribution_link.url)
        if save_to:
            file_path = os.path.join(save_to, distribution_link.basename)
            return self._save_data(request.content, file_path, md5_check=distribution_link.md5_digest)
        else:
            return request.content

    def has_package(self, package_name, version=None):
        if not version:
            return package_name in self.package_names()

        return len([l for l in self.download_links(package_name) if l.version==version]) > 0

    @property
    def upload_url(self):
        return '%s/' % self.uri.rstrip('/')

    def as_password_manager(self):
        mgr = urllib2.HTTPPasswordMgrWithDefaultRealm()
        mgr.add_password(None, self.uri, self.username, self.password)
        return mgr

    def __repr__(self):
        return '<Repository: %s>' % self.uri
