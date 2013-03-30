import os
import sys
import collections
import pkg_resources
from .dist import Distribution
from .upload import Uploader
from .exceptions import InvalidDistribution
from .status import NothingReporter
from .remote import RemoteDistribution

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

    def sync_distribution(self, dist_link):
        self.ui.report('version %s:' % dist_link.version, level=1)
        self.ui.inline('fetching...')
        try:
            distribution = dist_link.download(save_to=self.tmp_dir)
            self.ui.inline('registering...')
            self.destination.register(distribution)
            self.ui.inline('uploading...')
            self.destination.upload(distribution)
            cleaned = self._cleanup(distribution.path)
            if not cleaned:
                self.ui.inline('cannot remove %s ' % downloaded_dist)
        except InvalidDistribution, e:
            self.ui.error('Cannot parse metadata from %s' % e.args[0])

    def _package_name(self, spec):
        parsed = pkg_resources.Requirement.parse(spec)
        return parsed.project_name

    def sync(self):
        """
        Iterate alphabetically across each package in
        self.include.distribution_links() and for each of the DistributionLink
        objects generated synchronise the package to the self.destination
        repository, if the file does not already exist there.
        """
        for spec in sorted(self.include):
            package_name = self._package_name(spec)
            self.ui.report('Checking required versions for %s...' % package_name)

            exclude = list(self.exclude.specs_for(package_name))

            source_distributions = self.source.distributions(spec, exclude=exclude)
            if source_distributions:
                destination_distributions = self.destination.distributions(spec, exclude=exclude)
                to_sync = RemoteDistribution.diff(source_distributions, destination_distributions)
            else: # save making an unnecessary request to the destination repo
                to_sync = []

            if not to_sync:
                self.ui.inline('up to date.')
                continue

            self.ui.inline('%s required' % ', '.join([v.version for v in to_sync]))

            for dist_link in to_sync:
                self.sync_distribution(dist_link)
