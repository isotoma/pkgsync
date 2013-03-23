from unittest2 import TestCase
from StringIO import StringIO
from textwrap import dedent

from pkgsync.versions import Versions

class VersionsTest(TestCase):

    def _make_fp(self, content):
        test_cfg = StringIO()
        test_cfg.write(dedent(content))
        test_cfg.seek(0)
        return test_cfg

    def test_simple(self):
        fp = self._make_fp('''
            [versions]
            isotoma.recipe.django = 3.1.5
            Django = 1.4.5
        ''')

        v = Versions.from_cfg_fp(fp)
        self.assertEqual(len(v), 2)
        self.assertTrue('isotoma.recipe.django==3.1.5' in v)
        self.assertTrue('Django==1.4.5' in v)

    def test_custom_name(self):
        fp = self._make_fp('''
            [buildout]
            versions = loldongs

            [loldongs]
            isotoma.recipe.apache = 1.0.3
            missingbits = 0.0.16
        ''')
        v = Versions.from_cfg_fp(fp)
        self.assertEqual(len(v), 2)
        self.assertTrue('isotoma.recipe.apache==1.0.3' in v)
        self.assertTrue('missingbits==0.0.16' in v)

    def test_no_fetchers(self):
        temp = Versions.config_fetchers
        Versions.config_fetchers = []
        with self.assertRaises(RuntimeError):
            Versions.from_uri('')

    def test_specs_for(self):
        versions = Versions(['foo<1.2.3', 'bar<1.2.3'])
        specs_for = versions.specs_for('foo')
        self.assertEquals(specs_for.next(), 'foo<1.2.3')
        with self.assertRaises(StopIteration):
            specs_for.next()

    def test_multiple_specs_for(self):
        versions = Versions(['foo<1.2.3', 'foo<1.2.4'])
        specs_for = list(versions.specs_for('foo'))
        self.assertEquals(len(specs_for), 2)
        self.assertTrue('foo<1.2.3' in specs_for)
        self.assertTrue('foo<1.2.4' in specs_for)
