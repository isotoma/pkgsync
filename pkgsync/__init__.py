import getpass
import logging
import sys
from .sync import Sync
from .repo import Repository
from .status import StatusReporter
from .versions import Versions

from optparse import OptionParser

def parse_options():
    parser = OptionParser(
        usage='%prog --destination-url=https://eggsample.com ' \
              '--destination-username=youruser ' \
              '[package another==1.2 \'another<2.3,>1.2.4\'|--all-packages]'
    )
    parser.add_option(
        '-a', '--all-packages', dest='all_packages', action='store_true',
        help='Synchronise every package between the two repositories',
        default=False,
    )
    parser.add_option(
        '-e', '--exclude', dest='exclude', action='append', default=[],
        help='Do not synchronise this package between the repositories'
    )

    parser.add_option(
        '--source-url', dest='source_url', default='http://pypi.python.org',
        help='The source repository - where packages will be fetched from',
    )
    parser.add_option(
        '--source-username', dest='source_username',
        help='The optional username required to access the source repo',
    )
    parser.add_option(
        '--source-password', dest='source_password',
        help='Will prompt if --source-username is provided and this option is not',
    )

    parser.add_option(
        '--destination-url', dest='destination_url',
        help='The destination repository url - where packages will be uploaded to',
    )
    parser.add_option(
        '--destination-username', dest='destination_username',
        help='The optional username required to access the destination repo',
    )
    parser.add_option(
        '--destination-password', dest='destination_password',
        help='Will prompt if --destination-username is provided and this option is not',
    )

    parser.add_option(
        '--from-versions-file', dest='versions_file',
        help='Synchronise names and versions from a cfg file with a [versions] ' \
             'section. Intended for use with buildout configurations.'
    )

    parser.add_option(
        '--latest', dest='latest', action='store_true', default=False,
        help='Only synchronise the latest (highest) version available within a ' \
             'package specification, e.g. if you specify Django>1.4,<1.5 and ' \
             '1.4.3, 1.4.4 and 1.4.5 are available, only 1.4.5 is synchronised',
    )

    options, args = parser.parse_args()

    required = ('destination_url', 'destination_username')
    for r in required:
        if not hasattr(options, r):
            parser.print_help()
            raise SystemExit('You must provide a destination url, and a destination username')

    if not options.all_packages:
        if not len(args):
            parser.print_help()
            raise SystemExit('You must either specify --all or specify individual package names')

    return options, args

def configure_repository(url, username=None, password=None):
    if username and not password:
        password = getpass.getpass("Enter %s's password for %s >" % (username, url))
    return Repository(url, username=username, password=password)

def main():
    options, args = parse_options()

    logger = logging.getLogger(__name__)

    source = configure_repository(options.source_url, options.source_username, options.source_password)
    destination = configure_repository(options.destination_url, options.destination_username, options.destination_password)

    ui = StatusReporter()

    if options.all_packages:
        ui.report('Synchronising all packages...')
        include_versions = Versions.all_packages(source)
    elif options.versions_file:
        ui.report('Synchronising packages from %s' % options.versions_file)
        include_versions = Versions.from_uri(options.versions_file, source)
    else:
        ui.report('Synchronising packages: %r...' % args)
        include_versions = Versions(args, source)

    include_versions.latest = options.latest

    sync = Sync(
        source, destination, ui=ui,
        exclude=Versions(options.exclude, source),
        include=include_versions,
    )
    sync.sync()
