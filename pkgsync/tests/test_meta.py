from unittest2 import TestCase
import mock

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
