import tempfile
from pkgsync.digest import IteratingMd5Checker, Md5MismatchException
from unittest2 import TestCase

class IteratingMd5CheckerTest(TestCase):

    def setUp(self):
        self.valid_sum = '9f8d067fdb2373a64b4c3e420f31f4cc'
        self.valid_file = tempfile.NamedTemporaryFile()
        self.valid_file.write('loldongs\n')
        self.valid_file.flush()

        self.invalid_file = tempfile.NamedTemporaryFile()
        self.invalid_file.write('some other string')
        self.invalid_file.flush()

    def test_valid_sum(self):
        checker = IteratingMd5Checker(self.valid_file.name, self.valid_sum)
        checker.check()

    def test_invalid_sum(self):
        checker = IteratingMd5Checker(self.invalid_file.name, self.valid_sum)
        with self.assertRaises(Md5MismatchException):
            checker.check()
