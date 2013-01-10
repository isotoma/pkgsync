=======
pkgsync
=======

Overview
========

pkgsync is a tool used to move python packages from one repository to another.
Say, for example you use a pypi-clone application such as `chishop
<https://github.com/ask/chishop>`_ and you want to synchronise some packages
from pypi to it, or you have multiple pypi clone applications, etc.

This makes sure that all the versions of some package on repository A are
copied to repository B if they don't already exist on B.

Benefits
--------

pkgsync is particularly useful because it uses
`pkginfo <http://pypi.python.org/pypi/pkginfo>`_ to introspect packages so you
don't have to::

    $ tar zxf something-1.2.3.tar.gz
    $ cd something-1.2.3/
    $ python setup.py sdist register upload -r privaterepo

which is flawed for being slow and often showing up issues where people have
packaged their software incorrectly, with missing MANIFEST.in files, etc., plus
dates change, md5sums change... in short it's messy. Using pkgsync is less-so.

Password-Protected Repositories
-------------------------------

Supports upload and download authentication just in case you have a password-
protected private repository to copy from/to.

Usage
=====

Default ``--source-url`` is http://pypi.python.org since that's probably your use
-case.

If ``--destination-username`` is provided and ``--destination-password`` is not,
you'll be prompted for a password.

Full command-line options documentation available by doing ``pkgsync --help``

Example usage::

    pkgsync --destination-url=https://eggsample.com --destination-username=youruser tzinfo Django celery

Full repository sync::

    pkgsync --source-url=https://eggsample.com --destination-url=https://newrepo.com --destination-username=youruser --all


Development Instructions
========================

It's a pretty typical zc.buildout setup::

    $ python bootstrap.py
    $ bin/buildout

    $ bin/pkginfo --help
