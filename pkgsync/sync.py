import os
import sys
from .dist import Distribution
from .upload import Uploader
from .exceptions import InvalidDistribution
from .status import NothingReporter

class Sync(object):

    def __init__(self, source, destination, exclude=[], include=[], tmp_dir='/tmp', ui=NothingReporter()):
        """ By default looks for an exclude blacklist, but if the include kwarg
        is passed then whitelist mode is enabled and we only download those
        packages """
        self.source = source
        self.destination = destination
        self.exclude = exclude
        self.include = include
        self.tmp_dir = tmp_dir
        self.ui = ui

    def _package_list(self):
        if self.include:
            return self.include
        else:
            return [p for p in self.source.package_names() if not p in self.exclude]

    def _cleanup(self, path):
        self.ui.inline('cleaning up...')
        try:
            os.unlink(path)
            return True
        except OSError, IOError:
            return False

    def status(self, message, newline=None):
        if newline:
            print message
        else:
            print message,
        sys.stdout.flush()

    def required_versions(self, package_name):
        source_versions = self.source.download_links(package_name)
        destination_versions = list(self.destination.download_links(package_name))
        for sv in source_versions:
            match_found = False
            for dv in destination_versions:
                if dv.version == sv.version:
                    match_found = True
            if not match_found:
                yield sv

    def sync(self):
        for package_name in self._package_list():
            self.ui.report('Checking required versions for %s...' % package_name)
            versions = list(self.required_versions(package_name))
            if not versions:
                self.ui.inline('up to date.')
                continue
            self.ui.inline('%s required' % ', '.join([v.version for v in versions]))
            for version in self.required_versions(package_name):
                self.ui.report('version %s:' % version.version, level=1)
                self.ui.inline('fetching...')
                downloaded_dist = self.source.fetch(version, save_to=self.tmp_dir)
                try:
                    distribution = Distribution(downloaded_dist)
                    uploader = Uploader(self.destination, distribution)
                    self.ui.inline('registering...')
                    uploader.register()
                    self.ui.inline('uploading...')
                    uploader.upload()
                except InvalidDistribution, e:
                    self.ui.error('ERROR: Cannot parse metadata from %s' % e.args[0])

                cleaned = self._cleanup(downloaded_dist)
                if not cleaned:
                    self.ui.inline('cannot remove %s ' % downloaded_dist)
