import os
import sys
from .dist import Distribution
from .upload import Uploader

class Sync(object):

    def __init__(self, source, destination, exclude=[], include=[], tmp_dir='/tmp'):
        """ By default looks for an exclude blacklist, but if the include kwarg
        is passed then whitelist mode is enabled and we only download those
        packages """
        self.source = source
        self.destination = destination
        self.exclude = exclude
        self.include = include
        self.tmp_dir = tmp_dir

    def _package_list(self):
        if self.include:
            return self.include
        else:
            return [p for p in self.source.package_names() if not p in self.exclude]

    def _cleanup(self, distribution):
        try:
            os.unlink(distribution.path)
            return True
        except OSError, IOError:
            return False

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
            print 'Checking required versions for %s...' % package_name,
            versions = list(self.required_versions(package_name))
            if not versions:
                print 'up to date.'
                continue
            print '%s required' % ', '.join([v.version for v in versions])
            for version in self.required_versions(package_name):
                print '  fetching version %s...' % version.version,
                downloaded_dist = self.source.fetch(version, save_to=self.tmp_dir)
                print 'done.'
                self.distribution = Distribution(downloaded_dist)
                uploader = Uploader(self.destination, self.distribution)
                print '  registering version %s...' % version.version,
                uploader.register()
                print 'done.'
                print '  uploading version %s...' % version.version,
                uploader.upload()
                print 'done.'
                print '  cleaning up...',
                self._cleanup(self.distribution)
                print 'done.'
                print '  --'
