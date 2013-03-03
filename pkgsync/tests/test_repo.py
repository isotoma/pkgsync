from unittest2 import TestCase
from pkgsync.repo import Repository
import mock

class RepoTestCase(TestCase):

    def setUp(self):
        patcher = mock.patch('pkgsync.repo.requests')
        self.requests = patcher.start()
        self.addCleanup(patcher.stop)
        self.pkgsync_links = '''<html><head><title>Links for pkgsync</title></head>
            <body><h1>Links for pkgsync</h1>
            <a href="../../packages/source/d/pkgsync/pkgsync-0.0.1.tar.gz#md5=abcdefghijklmnopqrstuvwxyz012345">pkgsync-0.0.1.tar.gz</a><br/>
            <a href="../../packages/2.7/p/pkgsync/pkgsync-0.0.1-py2.7.egg#md5=abcdefghijklmnopqrstuvwxyz012345">pkgsync-0.0.1-py2.7.egg</a><br/>
            <a href="../../packages/source/d/pkgsync/pkgsync-0.0.0.tar.gz#md5=abcdefghijklmnopqrstuvwxyz012345">pkgsync-0.0.0.tar.gz</a><br/>
            <a href="https://github.com/isotoma/pkgsync" rel="homepage">0.0.1 home_page</a><br/>
            <a href="https://github.com/isotoma/pkgsync" rel="homepage">0.0.0 home_page</a><br/>
            </body></html>
        '''

    def test_package_index(self):
        repository = Repository('http://pypi.python.org')
        self.assertEqual(repository.package_index('some-example'), 'http://pypi.python.org/simple/some-example/')

    def test_index_simple_name(self):
        repository = Repository('http://pypi.python.org', simple_prefix='index')
        self.assertEqual(repository.package_index('some-example'), 'http://pypi.python.org/simple/some-example/')

    def test_user_pass(self):
        noauth_response = mock.Mock(status_code=401)
        unauth_response = mock.Mock(status_code=403)
        auth_response = mock.Mock(status_code=200)

        self.requests.get.return_value = noauth_response
        repository = Repository('http://pypi.python.org')

        with self.assertRaises(RuntimeError):
            repository.get('http://pypi.python.org/simple/')

        self.requests.get.return_value = unauth_response
        repository = Repository('http://pypi.python.org')

        with self.assertRaises(RuntimeError):
            repository.get('http://pypi.python.org/simple/')

        self.requests.get.return_value = auth_response
        repository.get('http://pypi.python.org/simple/')

    def test_no_links_all(self):
        response = mock.Mock(status_code=404)
        self.requests.get.return_value = response
        repo = Repository('http://pypi.python.org')
        dists = repo.all_distributions('foo')
        with self.assertRaises(StopIteration):
            dists.next()

    def test_no_links_spec(self):
        response = mock.Mock(status_code=404)
        self.requests.get.return_value = response
        repo = Repository('http://pypi.python.org')
        dists = repo.distributions('example<2.1.4')
        with self.assertRaises(StopIteration):
            dists.next()

    def test_no_links_latest_spec(self):
        response = mock.Mock(status_code=404)
        self.requests.get.return_value = response
        repo = Repository('http://pypi.python.org')
        dists = repo.distributions('example<2.1.4', latest=True)
        with self.assertRaises(StopIteration):
            dists.next()

    def test_all_distributions(self):
        package_page = mock.Mock(content=self.pkgsync_links)
        self.requests.get.return_value = package_page
        repo = Repository('http://pypi.python.org')

        dists = list(repo.all_distributions('pkgsync'))
        self.assertEqual(len(dists), 3)
        self.assertTrue('0.0.0' in [d.version for d in dists])
        self.assertTrue('0.0.1' in [d.version for d in dists])

    def test_spec_distributions(self):
        package_page = mock.Mock(content=self.pkgsync_links)
        self.requests.get.return_value = package_page
        repo = Repository('http://pypi.python.org')

        dists = list(repo.distributions('pkgsync>0.0.0'))
        self.assertEqual(len(dists), 2)
        self.assertEqual(dists[0].version, '0.0.1')

    def test_spec_distributions_latest(self):
        package_page = mock.Mock(content=self.pkgsync_links)
        self.requests.get.return_value = package_page
        repo = Repository('http://pypi.python.org')

        dists = list(repo.distributions('pkgsync>=0.0.0'))
        self.assertEqual(len(dists), 3)

        dists = list(repo.distributions('pkgsync>=0.0.0', latest=True))
        self.assertEqual(len(dists), 1)
        self.assertEqual(dists[0].version, '0.0.1')
