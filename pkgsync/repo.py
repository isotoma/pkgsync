import urllib2
import pkg_resources
from xml.dom.minidom import parseString

import requests

from .exceptions import InvalidRemoteDistribution
from .remote import RemoteDistribution
from .upload import Uploader

class Repository(object):

    def __init__(self, uri, username=None, password=None, simple_prefix='simple', uploader=Uploader):
        """
        :param uri: Repository URL. Lolz.
        :param username: Username for http authentication
        :param password: Password for http authentication
        :param simple_prefix: The path under which packages are listed.
        :param uploader: `Uploader` or a class that implements its public methods.
        """
        self.username = username
        self.password = password

        self.authentication = username and password

        self.uri = uri
        self.simple_prefix = 'simple'

        self.uploader = uploader(self)

        self._package_names = []

    def get(self, url, **kwargs):
        if self.authentication:
            kwargs.setdefault('auth', self._auth)
        response = requests.get(url, **kwargs)
        if response.status_code == 401:
            raise RuntimeError('Incorrect username/password for %s' % url)
        if response.status_code == 403:
            raise RuntimeError('You do not have permission to access %s' % url)
        return response

    @property
    def _auth(self):
        return (self.username, self.password)

    def _simple_url(self):
        return '%s/%s' % (
            self.uri.rstrip('/'),
            self.simple_prefix,
        )

    def package_index(self, package_name):
        """
        :param package_name: The package name string.
        :return: The url at which the distributions for a given package name
            are listed and linked to.
        """
        return '%s/%s/' % (
            self._simple_url(),
            package_name,
        )

    def all_distributions(self, package_name):
        """
        :param package_name: The name of a package.
        :returns: A `RemoteDistribution` object for every distribution
            available for the given package name.

        :note: To restrict the `RemoteDistribution` objects to a particular
            release specification, such as ``pkgsync>0.1``, use the
            `Repository.distributions` method.
        """
        request = self.get(self.package_index(package_name))
        if request.status_code == 404:
            raise StopIteration()

        dom = parseString(request.content)
        for link in dom.getElementsByTagName('a'):
            try:
                path = link.attributes['href'].value
                yield RemoteDistribution(self, path, package_name)
            except InvalidRemoteDistribution:
                continue # ignore the link and move on

    def distributions(self, spec, latest=False):
        """
        :param spec: A specification string describing one or more package
            releases, such as "pkgsync>0.1.0,<0.3.0" or "pkgsync==0.1.0".
        :return: yields `RemoteDistribution` objects for each distribution
            matching the given release specification.
        """
        parsed_spec = pkg_resources.Requirement.parse(spec)
        package_name = parsed_spec.project_name

        all_dists = self.all_distributions(package_name)

        if latest:
            try:
                yield max(all_dists, key=lambda d: pkg_resources.parse_version(d.version))
            except ValueError: # there are no dists
                pass
            raise StopIteration()

        for remote_dist in all_dists:
            if remote_dist.version in parsed_spec:
                yield remote_dist

    def packages(self):
        """ :return: A list of the name of every package in this repo """
        if not self._package_names:
            response = self.get(self._simple_url())
            dom = parseString(response.content)
            self._package_names = [e.firstChild.data for e in dom.getElementsByTagName('a')]
        return self._package_names

    def register(self, distribution):
        """ Register the given distribution to this package repository

        :param distribution: A `Distribution` object
        """
        return self.uploader.register(distribution)

    def upload(self, distribution):
        """ Upload the given distribution to this package repository

        :param distribution: A `Distribution` object
        """
        return self.uploader.upload(distribution)

    @property
    def upload_url(self):
        return '%s/' % self.uri.rstrip('/')

    def as_password_manager(self):
        """
        :return: A urllib2 password manager object for this repository, for use
            with the distutils-compatible urllib2 registration and upload
            commands.
        """
        mgr = urllib2.HTTPPasswordMgrWithDefaultRealm()
        mgr.add_password(None, self.uri, self.username, self.password)
        return mgr

    def __repr__(self):
        return '<Repository: %s>' % self.uri
