import os
import sys
import collections
from .dist import Distribution
from .upload import Uploader
from .exceptions import InvalidDistribution
from .status import NothingReporter

class Sync(object):

    def __init__(self, source, destination, exclude=[], include=[], tmp_dir='/tmp', ui=NothingReporter()):
        """
        By default looks for an exclude blacklist, but if the include kwarg is
        passed then whitelist mode is enabled and we only download those
        packages.

        Both include and exclude can be passed in either of the following forms:

            1. ``('Django', 'apache-libcloud')``
            2. ``{'Django': ['1.4.1', '1.3.2'], 'apache-libcloud': []}``

        In example 1, all available versions of Django and apache-libcloud will
        be synchronised. In example 2, all versions of apache-libcloud will be
        synchronised but only Django versions 1.4.1 and 1.3.2.
        """
        self.source = source
        self.destination = destination
        self.exclude = self._dictify(exclude)
        self.include = self._dictify(include)
        self.tmp_dir = tmp_dir
        self.ui = ui

    def _dictify(self, obj):
        if isinstance(obj, collections.Mapping):
            return obj
        return dict([(item, []) for item in obj])

    def _excluded(self, package_name):
        return (package_name in self.exclude.keys()) and \
               (not self.exclude[package_name])

    def _package_list(self):
        if self.include:
            for k in self.include.keys():
                if self._excluded(k):
                    del self.include[k]
            return self.include
        # if exclude specifies all versions of a package, skip it
        return dict([(p, []) for p in self.source.package_names()
                    if not self._excluded(p)])

    def _cleanup(self, path):
        self.ui.inline('cleaning up...')
        try:
            os.unlink(path)
            return True
        except OSError, IOError:
            return False

    def distribution_links(self, package_name, versions=()):
        source_versions = self.source.download_links(package_name, versions=versions)
        destination_versions = list(self.destination.download_links(package_name))
        for sv in source_versions:
            if sv.version in self.exclude.get(package_name, []):
                continue
            match_found = False
            for dv in destination_versions:
                if dv.version == sv.version:
                    match_found = True
            if not match_found:
                yield sv

    def sync(self):
        for package_name, required_versions in sorted(self._package_list().items(), key=lambda i: i[0]):
            self.ui.report('Checking required versions for %s...' % package_name)
            dist_links = list(self.distribution_links(package_name, required_versions))
            if not dist_links:
                self.ui.inline('up to date.')
                continue
            self.ui.inline('%s required' % ', '.join([v.version for v in dist_links]))
            for dist_link in dist_links:
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
