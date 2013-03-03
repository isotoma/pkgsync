import os
import mock
from unittest2 import TestCase

from pkgsync.meta import Metadata, OldStyleMetadata
from pkgsync.exceptions import InvalidDistribution

class OldStyleMetadataTest(TestCase):

    def test_valid_filename(self):
        distribution = mock.Mock(basename='OldStylePackage-1.2.3.tgz')
        metadata = OldStyleMetadata(distribution)
        self.assertEqual(metadata.name, 'OldStylePackage')
        self.assertEqual(metadata.version, '1.2.3')

    def test_invalid_filename(self):
        distribution = mock.Mock(basename='old')
        with self.assertRaises(InvalidDistribution):
            metadata = OldStyleMetadata(distribution)

    def test_register(self):
        distribution = mock.Mock(
            basename='OldStylePackage-1.2.3.tgz',
            md5_digest='0'*32,
            content=''
        )
        metadata = OldStyleMetadata(distribution)
        self.assertEqual(metadata.register(), {
            ':action': 'submit',
            'metadata_version' : '1.0',
            'name': 'OldStylePackage',
            'version': '1.2.3',
            'summary': 'UNKNOWN',
            'home_page': 'UNKNOWN',
            'author': 'UNKNOWN',
            'author_email': 'UNKNOWN',
            'license': 'UNKNOWN',
            'description': 'UNKNOWN',
            'keywords': [], 
            'platform': ['UNKNOWN'],
            'classifiers': (), 
            'download_url': 'UNKNOWN',
            'provides': (),
            'requires': (),
            'obsoletes': (),
        })

    def test_upload(self):
        distribution = mock.Mock(
            basename='OldStylePackage-1.2.3.tgz',
            md5_digest='0'*32,
            content=''
        )
        metadata = OldStyleMetadata(distribution)
        self.assertEqual(metadata.upload(), {
            ':action': 'file_upload',
            'protocol_version': '1',
            'name': 'OldStylePackage',
            'version': '1.2.3',
            'filetype': 'sdist',
            'pyversion': '',
            'md5_digest': '0'*32,
            'content': ('OldStylePackage-1.2.3.tgz', ''),
        })

    def test_beta_version(self):
        distribution = mock.Mock(basename='OldStylePackage-1.2.3-beta4.tgz')
        metadata = OldStyleMetadata(distribution)
        self.assertEqual(metadata.name, 'OldStylePackage')
        self.assertEqual(metadata.version, '1.2.3-beta4')


class MetadataTest(TestCase):

    def setUp(self):
        self.assets_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'assets')

    def asset_path(self, basename):
        return os.path.join(self.assets_path, basename)

    def test_invalid_dist(self):
        distribution = mock.Mock(path=self.asset_path('AnOldStylePackage-1.5.4.tar.gz'))
        with self.assertRaises(InvalidDistribution):
            metadata = Metadata(distribution)

    def test_upload(self):
        distribution = mock.Mock(
            path=self.asset_path('somefakepackage-0.0.0.tar.gz'),
            md5_digest='0'*32,
            basename='somefakepackage-0.0.0.tar.gz',
            content='',
        )
        metadata = Metadata(distribution)
        self.assertEqual(metadata.upload(), {
            ':action': 'file_upload',
            'protocol_version': '1',
            'name': 'somefakepackage',
            'version': '0.0.0',
            'filetype': 'sdist',
            'pyversion': '',
            'md5_digest': '0'*32,
            'content': ('somefakepackage-0.0.0.tar.gz', ''),
        })

    def test_register(self):
        distribution = mock.Mock(path=self.asset_path('somefakepackage-0.0.0.tar.gz'))
        metadata = Metadata(distribution)
        self.assertEqual(metadata.register(), {
            ':action': 'submit',
            'author': u'Eddy Merckx',
            'author_email': u'eddy.merckx@isotoma.com',
            'classifiers': (),
            'description': u'Long package description.',
            'download_url': 'UNKNOWN',
            'home_page': 'UNKNOWN',
            'keywords': [],
            'license': 'UNKNOWN',
            'metadata_version': u'1.0',
            'name': u'somefakepackage',
            'obsoletes': (),
            'platform': [u'UNKNOWN'],
            'provides': (),
            'requires': (),
            'summary': u'Package description',
            'version': u'0.0.0'
        })
