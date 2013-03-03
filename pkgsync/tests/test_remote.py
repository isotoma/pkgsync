from pkgsync.remote import RemoteDistribution
from unittest2 import TestCase
import tempfile
import shutil
import mock
import os

class RemoteDistributionTest(TestCase):

    def setUp(self):
        self.repo = mock.Mock()
        self.repo.package_index.return_value = 'https://example.com/simple/pkgsync/'
        self.empty_tgz = "\x1f\x8b\x08\x00\xd7\x8f2Q\x02\xff\xed\xc1\x01\r\x00\x00\x00\xc2\xa0\xf7Om\x0e7\xa0\x00\x00\x00\x00\x00\x00\x00\x00\x00\x807\x03\x9a\xde\x1d'\x00(\x00\x00"
        self.empty_digest = "94e4358a3df99f5b7b288b2352b6667b"
        mock_response = mock.Mock(content=self.empty_tgz)
        self.repo.get.return_value = mock_response
        self.dirs = []

    def cleanUp(self):
        for d in self.dirs:
            shutil.rmtree(d)

    def test_tgz_attributes(self):
        rd = RemoteDistribution(
            self.repo,
            '../../packages/source/p/pkgsync/pkgsync-0.1.0.tar.gz#md5=c264ffd778c274561842237d6253427a',
            'pkgsync'
        )
        self.assertEqual(rd.basename, 'pkgsync-0.1.0.tar.gz')
        self.assertEqual(rd.version, '0.1.0')
        self.assertEqual(rd.extension, '.tar.gz')
        self.assertEqual(rd.md5_digest, 'c264ffd778c274561842237d6253427a')
        self.assertEqual(rd.url, 'https://example.com/packages/source/p/pkgsync/pkgsync-0.1.0.tar.gz#md5=c264ffd778c274561842237d6253427a')

    def test_egg_attributes(self):
        rd = RemoteDistribution(
            self.repo,
            '../../packages/2.7/p/pkgsync/pkgsync-0.1.0-py2.7.egg#md5=ee6fbb8ee50e9b9d1bda8df6428090ca',
            'pkgsync',
        )
        self.assertEqual(rd.basename, 'pkgsync-0.1.0-py2.7.egg')
        self.assertEqual(rd.version, '0.1.0')
        self.assertEqual(rd.extension, '.egg')
        self.assertEqual(rd.md5_digest, 'ee6fbb8ee50e9b9d1bda8df6428090ca')
        self.assertEqual(rd.url, 'https://example.com/packages/2.7/p/pkgsync/pkgsync-0.1.0-py2.7.egg#md5=ee6fbb8ee50e9b9d1bda8df6428090ca')

    def test_no_md5(self):
        rd = RemoteDistribution(
            self.repo,
            '../../packages/2.7/p/pkgsync/pkgsync-0.1.0-py2.7.egg',
            'pkgsync',
        )
        self.assertEqual(rd.md5_digest, None)

    def test_download(self):
        test_dir = tempfile.mkdtemp()
        self.dirs.append(test_dir)
        rd = RemoteDistribution(
            self.repo,
            '../../packages/source/p/pkgsync/pkgsync-0.1.0.tar.gz#md5=%s' % self.empty_digest,
            'pkgsync',
        )
        dist = rd.download(save_to=test_dir)
        downloaded_file_path = os.path.join(test_dir, 'pkgsync-0.1.0.tar.gz')
        self.assertTrue(os.path.isfile(downloaded_file_path))
        self.assertEqual(dist.path, downloaded_file_path)
