import os
import sys
import collections
from .dist import Distribution
from .upload import Uploader
from .exceptions import InvalidDistribution
from .status import NothingReporter

class Sync(object):

    def __init__(self, source, destination, exclude, include, tmp_dir='/tmp', ui=NothingReporter()):
        """
        :param source: The Repository packages will be downloaded from
        :param destination: The Repository packages will be uploaded to
        :param exclude:
            A Versions object describing which packages should not be
            synchronised between the source and destination repositories.
        :param include:
            A Versions object describing which packages should be synchronised
            between the source and destination repository.
        :param tmp_dir:
            The directory that packages will be downloaded to before they are
            parsed and uploaded to the destination repository.
        :param ui:
            A StatusReporter class, defaulting to pkgsync.status.NothingReporter
            for which each output method is a no-op.
        """
        self.source = source
        self.destination = destination
        self.exclude = exclude
        self.include = include
        self.tmp_dir = tmp_dir
        self.ui = ui

    def _cleanup(self, path):
        self.ui.inline('cleaning up...')
        try:
            os.unlink(path)
            return True
        except OSError, IOError:
            return False

    def _dists_for_download(self, package_name):
        for dist_link in self.include[package_name]:

            if dist_link in self.exclude.get(package_name, []):
                continue
            if self.destination.has_package(package_name, dist_link.version):
                continue

            yield dist_link

    def _sync_distribution(self, dist_link):
        self.ui.report('version %s:' % dist_link.version, level=1)
        self.ui.inline('fetching...')
        downloaded_dist = self.source.fetch(dist_link, save_to=self.tmp_dir)
        try:
            distribution = Distribution(downloaded_dist)
            uploader = Uploader(self.destination, distribution)
            self.ui.inline('registering...')
            uploader.register()
            self.ui.inline('uploading...')
            uploader.upload()
        except InvalidDistribution, e:
            self.ui.error('Cannot parse metadata from %s' % e.args[0])

        cleaned = self._cleanup(downloaded_dist)
        if not cleaned:
            self.ui.inline('cannot remove %s ' % downloaded_dist)

    def sync(self):
        """
        Iterate alphabetically across each package in
        self.include.distribution_links() and for each of the DistributionLink
        objects generated synchronise the package to the self.destination
        repository, if the file does not already exist there.
        """
        for package_name in sorted(self.include.keys()):

            self.ui.report('Checking required versions for %s...' % package_name)
            to_sync = list(self._dists_for_download(package_name))
            if not to_sync:
                self.ui.inline('up to date.')
                continue

            self.ui.inline('%s required' % ', '.join([v.version for v in to_sync]))

            for dist_link in to_sync:
                self._sync_distribution(dist_link)
