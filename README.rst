=======
pkgsync
=======

Overview
========

pkgsync is two things: a command line utility for copying python packages from
one repository to another, ensuring that all distributions on the source repo
are present on the distribution repo. Secondly, pkgsync can also be used as a
library for registering, uploading, and downloading distributions from python
package repositories.

The primary use-case for the utility is if, for example, you use a pypi-clone
application such as `chishop <https://github.com/ask/chishop>`_ and you want to
synchronise some packages from pypi to it, or you have multiple pypi clone
applications that you wish to keep synchronised, etc.

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

Old-Style Packages
------------------

Very naively support for old-style packages - packages without any setuptools
metadata in them. For these packages, we attempt to use the filename to
determine the package name and release, then register the package using
the value 'UNKNOWN' for all the other setuptools metadata (as per the spec).

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

Using the Library
=================

You can see which distributions are available on a given repository, and filter
them using the typical setup.py requirement specification format::

    >> from pkgsync.repo import Repository
    >> pypi = Repository('https://pypi.python.org')

    >> celery_dists = pypi.distributions('celery>=3.0.15')

    >> remote_distribution = celery_dists.next()
    >> remote_distribution.version
    u'3.0.15'
    >> remote_distribution.md5_digest
    u'5ac83d2cdcacf230897d9bffcf0ddbd9'

You can download any of the RemoteDistribution objects you wish::

    >> local_distribution = remote_distribution.download()
    >> local_distribution
    <Distribution: /tmp/celery-3.0.15.tar.gz>

View the metadata for Distributions::

    >> from pkgsync.dist import Distribution
    >> local_distribution = Distribution('/tmp/celery-3.0.15.tar.gz')

    >> local_distribution.meta.summary
    u'Distributed Task Queue'

    >> local_distribution.meta.classifiers[0]
    u'Development Status :: 5 - Production/Stable'

    >> local_distribution.meta.version
    u'3.0.15'

Register and upload new distributions::

    >> from pkgsync.repo import Repository
    >> from pkgsync.dist import Distribution

    >> distribution = Distribution('/tmp/loldongs-1.2.3.tar.gz')
    >> pypi = Repository('https://pypi.python.org', username='monty', password='farcicalaquaticceremony')

    >> pypi.register(distribution)
    (200, 'OK')

    >> pypi.upload(distribution)
    (200, 'OK')

AND MUCH, MUCH MORE.

Development Instructions
========================

It's a pretty typical zc.buildout setup::

    $ python bootstrap.py
    $ bin/buildout

    $ bin/pkginfo --help
