import os
from unittest2 import TestCase
from pkgsync.dist import Distribution

from pkgsync.meta import Metadata, OldStyleMetadata

class DistributionTest(TestCase):

    def setUp(self):
        self.assets_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'assets')

    def asset_path(self, basename):
        return os.path.join(self.assets_path, basename)

    def test_init_valid_source(self):
        """ Ensure that `Distribution` is selecting the correct metadata class """
        d = Distribution(self.asset_path('somefakepackage-0.0.0.tar.gz'))
        self.assertTrue(isinstance(d.meta, Metadata))

    def test_init_oldstyle(self):
        """ Ensure that `Distribution` is selecting the correct metadata class """
        d = Distribution(self.asset_path('AnOldStylePackage-1.5.4.tar.gz'))
        self.assertTrue(isinstance(d.meta, OldStyleMetadata))

    def test_init_oldstyle_beta(self):
        d = Distribution(self.asset_path('AnOldStylePackage-1.2.1-beta3.tar.gz'))
        self.assertTrue(isinstance(d.meta, OldStyleMetadata))

    def test_content(self):
        d = Distribution(self.asset_path('somefakepackage-0.0.0.tar.gz'))
        self.assertEqual(len(d.content), 906)

    def test_md5_digest(self):
        d = Distribution(self.asset_path('somefakepackage-0.0.0.tar.gz'))
        self.assertEqual(d.md5_digest, '22ed441feb4fbfaf700b36260195b986')
