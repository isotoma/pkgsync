from unittest2 import TestCase
import tempfile
import mock

from pkgsync.cfg import ConfigFetcher, LocalConfigFetcher, HttpConfigFetcher

class ConfigFetcherTest(TestCase):

    def test_abstract(self):
        with self.assertRaises(NotImplementedError):
            c = ConfigFetcher('')
            c.fetch()

class LocalConfigFetcherTest(TestCase):

    def test_fetch_from_slash(self):
        f = tempfile.NamedTemporaryFile()
        fetcher = LocalConfigFetcher(f.name)
        self.assertNotEqual(fetcher.fetch(), None)
        f.close()

    def test_fetch_file_scheme(self):
        f = tempfile.NamedTemporaryFile()
        fetcher = LocalConfigFetcher('file://%s' % f.name)
        self.assertNotEqual(fetcher.fetch(), None)
        f.close()

    def test_fetch_nonexistent(self):
        fetcher = LocalConfigFetcher('/foobarbazqux')
        self.assertEqual(fetcher.fetch(), None)

    def test_fetch_http(self):
        fetcher = LocalConfigFetcher('https://foo.com/bar.cfg')
        self.assertEqual(fetcher.fetch(), None)


class HttpConfigFetcherTest(TestCase):

    def setUp(self):
        patcher = mock.patch('pkgsync.cfg.requests')
        self.requests = patcher.start()
        self.addCleanup(patcher.stop)

    def test_invalid_uri(self):
        f = HttpConfigFetcher('ftp://lol.com/foo.cfg')
        self.assertEqual(f.fetch(), None)

    def test_valid_http_uri(self):
        self.requests.get.return_value = mock.Mock(status_code=200)
        f = HttpConfigFetcher('http://foo.com')
        fetched = f.fetch()
        self.assertNotEqual(fetched, None)
        self.assertTrue(hasattr(fetched, 'readline'))

    def test_valid_https_uri(self):
        self.requests.get.return_value = mock.Mock(status_code=200)
        f = HttpConfigFetcher('https://foo.com')
        fetched = f.fetch()
        self.assertNotEqual(fetched, None)
        self.assertTrue(hasattr(fetched, 'readline'))

    def test_unauthorised(self):
        self.requests.get.return_value = mock.Mock(status_code=401)
        f = HttpConfigFetcher('http://foo.com/bar.cfg')
        with self.assertRaises(RuntimeError):
            f.fetch()
